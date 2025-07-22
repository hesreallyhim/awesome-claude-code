# Guitar Development Guide

## Build Commands
- Setup dependencies: `sudo apt install build-essential ruby qmake6 libqt6core6 libqt6gui6 libqt6svg6-dev libqt6core5compat6-dev zlib1g-dev libgl1-mesa-dev libssl-dev`
- Prepare environment: `ruby prepare.rb`
- Build project: `mkdir build && cd build && qmake6 ../Guitar.pro && make -j8`
- Release build: `qmake "CONFIG+=release" ../Guitar.pro && make`
- Debug build: `qmake "CONFIG+=debug" ../Guitar.pro && make`

## Code Style Guidelines
- C++17 standard with Qt 6 framework
- Classes use PascalCase naming (MainWindow, GitCommandRunner)
- Methods use camelCase naming (openRepository, setCurrentBranch)
- Private member variables use _ suffix or m pointer (data_, m)
- Constants and enums use UPPER_CASE or PascalCase
- Include order: class header, UI header, project headers, Qt headers, standard headers
- Error handling: prefer return values for operations that can fail
- Whitespace: tabs for indentation, spaces for alignment
- Line endings: LF (\n)
- Max line length: no limits
- Use Qt's signal/slot mechanism for async operations
