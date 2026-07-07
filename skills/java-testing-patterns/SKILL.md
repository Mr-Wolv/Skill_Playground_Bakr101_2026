---
name: java-testing-patterns
description: JUnit 5, Mockito, Spring Boot Test, Testcontainers — Java testing best practices
---

# Java Testing Patterns

Testing patterns for Java applications across unit, integration, and end-to-end levels.

## When to use

- Writing tests for Java / Spring Boot applications
- Need Mockito mocks or Spring Boot Test slices
- Integration testing with real databases via Testcontainers

## Instructions

1. **Identify the test level**:
   - **Unit**: Test a single class with mocked dependencies (JUnit 5 + Mockito)
   - **Slice**: Test a specific layer with `@WebMvcTest`, `@DataJpaTest`
   - **Integration**: Test the full context with `@SpringBootTest`
2. **Set up test structure** — follow the project's existing test conventions
3. **Write tests** covering happy path, error cases, edge cases
4. **Use Testcontainers** for real database/queue integration tests
5. **Assert correctly** — use AssertJ for fluent assertions

## Example

```java
@SpringBootTest
@Testcontainers
class UserRepositoryTest {

  @Container
  static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");

  @DynamicPropertySource
  static void configure(DynamicPropertyRegistry reg) {
    reg.add("spring.datasource.url", postgres::getJdbcUrl);
  }

  @Autowired
  private UserRepository repository;

  @Test
  void shouldSaveAndFindUser() {
    var user = new User("test@example.com", "Test");
    repository.save(user);

    var found = repository.findByEmail("test@example.com");
    assertThat(found).isPresent();
    assertThat(found.get().getName()).isEqualTo("Test");
  }
}
```

## Edge cases

- Transactional test cleanup (use `@Transactional` where appropriate)
- Parallel test execution (ensure database isolation)
- Time-dependent logic (use `Clock` injection for testability)
