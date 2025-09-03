import ctypes
import ctypes.wintypes as wintypes
import psutil
import os
import threading
import time

PROCESS_ALL_ACCESS = 0x1F0FFF

# Offsets
OFFSETS = {
    "Money": 0x28CAD4,
    "Diamonds": 0x28CAEC,
    "Gas": [0x28CA2C, 0x2A8]
}

OpenProcess = ctypes.windll.kernel32.OpenProcess
ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
WriteProcessMemory = ctypes.windll.kernel32.WriteProcessMemory
CloseHandle = ctypes.windll.kernel32.CloseHandle

FLOAT = ctypes.c_float
UINT64 = ctypes.c_uint64


def get_pid(process_name: str):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            return proc.info['pid']
    return None


def get_module_base(pid: int, module_name: str):
    TH32CS_SNAPMODULE = 0x00000008
    h_snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pid)

    class MODULEENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("th32ModuleID", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("GlblcntUsage", wintypes.DWORD),
            ("ProccntUsage", wintypes.DWORD),
            ("modBaseAddr", ctypes.POINTER(ctypes.c_byte)),
            ("modBaseSize", wintypes.DWORD),
            ("hModule", wintypes.HMODULE),
            ("szModule", ctypes.c_char * 256),
            ("szExePath", ctypes.c_char * wintypes.MAX_PATH),
        ]

    me32 = MODULEENTRY32()
    me32.dwSize = ctypes.sizeof(MODULEENTRY32)

    Module32First = ctypes.windll.kernel32.Module32First
    Module32Next = ctypes.windll.kernel32.Module32Next

    if not Module32First(h_snapshot, ctypes.byref(me32)):
        CloseHandle(h_snapshot)
        return None

    while True:
        if me32.szModule.decode("utf-8") == module_name:
            base_addr = ctypes.addressof(me32.modBaseAddr.contents)
            CloseHandle(h_snapshot)
            return base_addr
        if not Module32Next(h_snapshot, ctypes.byref(me32)):
            break

    CloseHandle(h_snapshot)
    return None


def read_memory_float(h_process, address):
    buffer = FLOAT()
    bytes_read = ctypes.c_size_t()
    success = ReadProcessMemory(h_process,
                                ctypes.c_void_p(address),
                                ctypes.byref(buffer),
                                ctypes.sizeof(buffer),
                                ctypes.byref(bytes_read))
    if success:
        return buffer.value
    return None


def write_memory_float(h_process, address, value: float):
    buffer = FLOAT(value)
    bytes_written = ctypes.c_size_t()
    success = WriteProcessMemory(h_process,
                                 ctypes.c_void_p(address),
                                 ctypes.byref(buffer),
                                 ctypes.sizeof(buffer),
                                 ctypes.byref(bytes_written))
    return success != 0


def get_pointer_address(h_process, base, offsets):
    addr = base
    buffer = UINT64()
    bytes_read = ctypes.c_size_t()
    for offset in offsets[:-1]:
        ReadProcessMemory(h_process, ctypes.c_void_p(addr + offset),
                          ctypes.byref(buffer), ctypes.sizeof(buffer), ctypes.byref(bytes_read))
        addr = buffer.value
    return addr + offsets[-1]


def gas_freezer(h_process, gas_addr):
    while True:
        current = read_memory_float(h_process, gas_addr)
        if current != 100.0:
            write_memory_float(h_process, gas_addr, 100.0)
        time.sleep(0.0005)


def main():
    PROCESS_NAME = "HillClimbRacing.exe"

    pid = get_pid(PROCESS_NAME)
    if not pid:
        print(f"[!] {PROCESS_NAME} not found")
        return

    base_addr = get_module_base(pid, PROCESS_NAME)
    if not base_addr:
        print(f"[!] Failed to get module base for {PROCESS_NAME}")
        return

    h_process = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h_process:
        print("[!] Failed to open process")
        return

    print(f"[+] Attached to {PROCESS_NAME} (PID: {pid}, Base: 0x{base_addr:X})")

    gas_addr = get_pointer_address(h_process, base_addr, OFFSETS["Gas"])

    threading.Thread(target=gas_freezer, args=(h_process, gas_addr), daemon=True).start()

    try:
        while True:
            os.system("cls")
            print("=== Hill Climb Racing Trainer ===")
            print("1. Set Money")
            print("2. Set Diamonds")
            print("3. Exit")
            choice = input("\nSelect an option: ").strip()

            if choice == "1":
                value = int(input("Enter new Money value: "))
                addr = base_addr + OFFSETS["Money"]
                if write_memory_float(h_process, addr, float(value)):
                    print(f"[+] Money set to {value}")
                else:
                    print("[!] Failed to write Money")
                input("Press Enter to continue...")

            elif choice == "2":
                value = int(input("Enter new Diamonds value: "))
                addr = base_addr + OFFSETS["Diamonds"]
                if write_memory_float(h_process, addr, float(value)):
                    print(f"[+] Diamonds set to {value}")
                else:
                    print("[!] Failed to write Diamonds")
                input("Press Enter to continue...")

            elif choice == "3":
                break

            else:
                print("[!] Invalid choice")
                input("Press Enter to continue...")

    finally:
        CloseHandle(h_process)


if __name__ == "__main__":
    main()
