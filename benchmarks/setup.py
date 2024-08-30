import os
import re
import shutil
import subprocess
import sysconfig
import sys

from setuptools import setup

import torch


class CMakeBuild():

    def __init__(self):
        self.current_dir = os.path.abspath(os.path.dirname(__file__))
        self.build_temp = self.current_dir + "/build/temp"
        self.extdir = self.current_dir + "/key_benchmarks/triton_kernels_benchmark"

    def run(self):
        try:
            out = subprocess.check_output(["cmake", "--version"])
        except OSError as error:
            raise RuntimeError("CMake must be installed") from error

        match = re.search(r"version\s*(?P<major>\d+)\.(?P<minor>\d+)([\d.]+)?", out.decode())
        cmake_major, cmake_minor = int(match.group("major")), int(match.group("minor"))
        if (cmake_major, cmake_minor) < (3, 18):
            raise RuntimeError("CMake >= 3.18.0 is required")

        self.build_extension()

    def build_extension(self):
        ninja_dir = shutil.which("ninja")
        # create build directories
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        # python directories
        python_include_dir = sysconfig.get_path("platinclude")
        cmake_args = [
            "-G",
            "Ninja",  # Ninja is much faster than make
            "-DCMAKE_MAKE_PROGRAM=" +
            ninja_dir,  # Pass explicit path to ninja otherwise cmake may cache a temporary path
            f"-DCMAKE_PREFIX_PATH={torch.utils.cmake_prefix_path}",
            "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
            "-DCMAKE_ARCHIVE_OUTPUT_DIRECTORY=" + self.extdir,
            "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=" + self.extdir,
            "-DPython3_EXECUTABLE:FILEPATH=" + sys.executable,
            "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON",
            "-DPYTHON_INCLUDE_DIRS=" + python_include_dir,
            "-DCMAKE_C_COMPILER=icx",
            "-DCMAKE_CXX_COMPILER=icpx",
        ]

        # configuration
        build_type = "Debug"
        build_args = ["--config", build_type]
        cmake_args += ["-DCMAKE_BUILD_TYPE=" + build_type]
        max_jobs = os.getenv("MAX_JOBS", str(2 * os.cpu_count()))
        build_args += ["-j" + max_jobs]

        env = os.environ.copy()
        cmake_dir = self.build_temp
        subprocess.check_call(["cmake", self.current_dir] + cmake_args, cwd=cmake_dir, env=env)
        subprocess.check_call(["cmake", "--build", "."] + build_args, cwd=cmake_dir)


cmake = CMakeBuild()
cmake.run()

setup(name="triton-kernels-benchmark", packages=[
    "triton_kernels_benchmark",
], package_dir={
    "triton_kernels_benchmark": "key_benchmarks/triton_kernels_benchmark",
}, package_data={"triton_kernels_benchmark": ["xetla_kernel.so"]})
