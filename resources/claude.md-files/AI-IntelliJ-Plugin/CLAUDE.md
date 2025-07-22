# AI Integration Plugin Development Guide

## Build Commands
- `./gradlew build` - Build the entire project
- `./gradlew test` - Run all tests
- `./gradlew test --tests "com.didalgo.intellij.chatgpt.chat.metadata.UsageAggregatorTest"` - Run a specific test class
- `./gradlew test --tests "*.StandardLanguageTest.testDetection"` - Run a specific test method
- `./gradlew runIde` - Run the plugin in a development IDE instance
- `./gradlew runPluginVerifier` - Verify plugin compatibility with different IDE versions
- `./gradlew koverReport` - Generate code coverage report

## Code Style Guidelines
- **Package Structure**: Use `com.didalgo.intellij.chatgpt` as base package
- **Imports**: Organize imports alphabetically; no wildcards; static imports last
- **Naming**: CamelCase for classes; camelCase for methods/variables; UPPER_SNAKE_CASE for constants
- **Types**: Use annotations (`@NotNull`, `@Nullable`) consistently; prefer interface types in declarations
- **Error Handling**: Use checked exceptions for recoverable errors; runtime exceptions for programming errors
- **Documentation**: Javadoc for public APIs; comment complex logic; keep code self-explanatory
- **Testing**: Write unit tests for all business logic; integration tests for UI components
- **Architecture**: Follow IDEA plugin architecture patterns; use services for global state

## Coding Patterns
- Use `ChatGptBundle` for internationalized strings
- Leverage IntelliJ Platform APIs when possible instead of custom implementations
- Use dependency injection via constructor parameters rather than service lookups