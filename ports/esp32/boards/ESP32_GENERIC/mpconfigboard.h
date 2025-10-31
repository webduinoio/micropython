// Both of these can be set by mpconfigboard.cmake if a BOARD_VARIANT is
// specified.

#ifndef MICROPY_HW_BOARD_NAME
#define MICROPY_HW_BOARD_NAME "Generic ESP32 module"
#endif

#ifndef MICROPY_HW_MCU_NAME
#define MICROPY_HW_MCU_NAME "ESP32"
#endif

// 禁用藍牙以節省記憶體和韌體空間
#define MICROPY_PY_BLUETOOTH (0)

// Python heap 設為 80KB，保留更多記憶體給 WiFi/MQTT
// 180KB 可用記憶體對 Python 應用已經足夠
#define MICROPY_GC_INITIAL_HEAP_SIZE (80 * 1024)
