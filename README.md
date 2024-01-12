# Bob Build System
Bob is a build system designed for compiling C/C++ projects and providing a consistent toolchain for developers. The goal is to eliminate the variability introduced by different software versions and configurations on individual machines. Bob achieves this by managing its own versions of libraries and compilers.

## Features
**Consistent Toolchain:** Bob ensures that all developers working on the project use the same toolchain, reducing compatibility issues and streamlining the build process.

**Self-contained:** Bob acquires and manages its own versions of libraries and compilers, eliminating the need for developers to install specific software on their machines.

**Ninja Build System:** Bob utilizes the Ninja build system to perform builds efficiently. Ninja is known for its speed and scalability, making it a suitable choice for large C/C++ projects.

**Windows EWDK:** Unlike Visual Studio, Bob acquires the complete Windows EWDK providing access to every header and library available for Windows.

**No Clang CL:** Bob uses the Clang compiler directly rather than relying on the Clang CL interface under Windows.

### Version 2 WIP
The initial attempt at the build system showed promise at first. However, with the gradual inclusion of additional libraries and the transition from using MSVC to Clang, it has become evident that Bob requires a comprehensive redesign.

The proposed plan is as follows:

* Subsitute the GN build with an entirely Python-based build system.
* Use the Python bootstrap at the commencement of the build process.
* Initiate the build system from the bootstrap rather than directly invoking ninja.
* Directly invoke Python tools from Ninja while being aware of inputs and outputs.
* Integrate a global mutex within the bootstrap for synchronization purposes rather than a modified version of Ninja.
* Implement directory monitoring for invalidations.
* Optimize disk space usage by recompressing downloaded caches wherever feasible.
* Extract only the essential components of libraries required for the build process.
* Restrict the building of third-party libraries to those essential for the build process.
