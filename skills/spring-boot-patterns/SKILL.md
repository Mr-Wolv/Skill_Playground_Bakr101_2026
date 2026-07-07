---
name: spring-boot-patterns
description: Spring Boot controllers, services, repositories, configuration, and dependency injection
---

# Spring Boot Patterns

Best practices for building Spring Boot applications with clean layering and testability.

## When to use

- Building a new Spring Boot service
- Refactoring an existing Spring project
- Code reviewing a Spring Boot application

## Instructions

1. **Follow the layered architecture**:
   - **Controller** — handles HTTP requests/responses, delegates to services
   - **Service** — contains business logic, uses repositories
   - **Repository** — data access (Spring Data JPA, JDBC)
2. **Use constructor injection** — prefer final fields + Lombok `@RequiredArgsConstructor`
3. **Keep controllers thin** — no business logic, just request parsing and response formatting
4. **Use DTOs** — don't expose entity classes directly to controllers
5. **Add validation** — use `@Valid` with Jakarta Bean Validation annotations
6. **Handle errors** — use `@ControllerAdvice` for consistent error responses

## Example

```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;

    @GetMapping("/{id}")
    public ResponseEntity<UserDto> getUser(@PathVariable UUID id) {
        return ResponseEntity.ok(userService.findById(id));
    }
}

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;

    public UserDto findById(UUID id) {
        return userRepository.findById(id)
            .map(UserDto::from)
            .orElseThrow(() -> new NotFoundException("User not found"));
    }
}
```

## Anti-patterns

- Field injection with `@Autowired` (harder to test)
- Business logic in controllers
- Exposing entities directly as API responses (couples API to DB schema)
- Ignoring transaction boundaries
