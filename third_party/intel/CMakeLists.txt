include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(${CMAKE_CURRENT_BINARY_DIR}/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/lib)
add_subdirectory(include)
add_subdirectory(lib)

add_triton_plugin(TritonXPU
  ${CMAKE_CURRENT_SOURCE_DIR}/triton_xpu.cc

  LINK_LIBS
  MLIRGPUToLLVMSPV
  PostProcessLLVMIR
  TritonGENToLLVM
  TritonGENToLLVMIRTranslation
  TritonIntelGPUToLLVM
  TritonIntelGPUTransforms
  TritonToTritonGPUWarp
)

if(TRITON_BUILD_UT)
  add_subdirectory(unittest)
endif()
