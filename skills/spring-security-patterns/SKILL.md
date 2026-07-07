---
name: spring-security-patterns
description: Firebase Auth, RBAC, tenant isolation, CORS, security filter chains
---

# Spring Security Patterns

Security configuration patterns for Spring Boot applications.

## When to use

- Setting up authentication and authorization in a Spring Boot app
- Adding Firebase Authentication to a backend
- Configuring CORS for frontend-backend communication
- Implementing multi-tenant isolation

## Instructions

1. **Configure the security filter chain** — order matters, most specific routes first
2. **Set up authentication**:
   - **Firebase Auth**: verify JWTs from Firebase, extract user identity
   - **JWT**: issue and validate custom JWTs with a secret or public key
   - **OAuth2**: delegate to an OAuth2 provider (Google, GitHub, etc.)
3. **Implement authorization** — RBAC with `@PreAuthorize` or security matchers
4. **Configure CORS** — allow specific origins, methods, and headers for frontend access
5. **Add tenant isolation** — extract tenant ID from JWT claims or subdomain, scope all queries

## Example

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .cors(Customizer.withDefaults())
            .csrf(AbstractHttpConfigurer::disable)
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .sessionManagement(sm -> sm.sessionCreationPolicy(STATELESS))
            .build();
    }
}
```

## Edge cases

- Token refresh flows (ensure refresh tokens are properly validated)
- CORS preflight requests (ensure OPTIONS requests are handled correctly)
- Multi-tenant data leakage (test that Tenant A can't see Tenant B's data)
- Rate limiting on auth endpoints (prevent brute force attacks)
