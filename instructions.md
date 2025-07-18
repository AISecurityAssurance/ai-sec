# Instructions
1) Read the project description in documentation/security-platform-complete-docs.md
2) Read the earlier version of the project description (security-platform-architecture.md).  Prefer Protocols for models and storage.
3) Read the template.html file.
4) Read the remainder of this document for context.

# Coding guidelines
- Always use SOLID design principles unless you have a REALLY good reason not to.
- Follow the guidelines for React JS (TS) components
- Follow guidelines for FastAPI
- Create a model agnostic approach, allowing users to substitute models on define any required interfaces.  Use Protocols, definning an interface that will: separate and return responses (text portion only), token stats (if available), define the propper formatting of inputs, properly set up the model client (API, auth, host, model name, etc. ) as needed.
- Create a file storage agnostic Protocol allowing for: in-house storage, cloud storage, proper set up (i.e., credentials, etc.)
- If you feel a class hierachy is more appropriate for the models and storage, that's an option. 

## Solid design principles
1. Single Responsibility Principle (SRP): A class should have only one reason to change. This means each class should have a single, well-defined responsibility. For example, a class responsible for both user authentication and sending welcome emails would violate SRP. 

2. Open/Closed Principle (OCP): Software entities (classes, modules, functions, etc.) should be open for extension, but closed for modification. This means you should be able to add new functionality without altering existing code. For example, instead of modifying a class to handle a new type of payment, you would extend it with a new class. 

3. Liskov Substitution Principle (LSP): Subtypes must be substitutable for their base types without altering the correctness of the program. In simpler terms, if a class B inherits from class A, you should be able to use an object of type B wherever an object of type A is expected without breaking the program. 

4. Interface Segregation Principle (ISP): Clients should not be forced to depend on methods they do not use. This principle encourages breaking down large interfaces into smaller, more specific ones. For example, a single interface with many methods should be split into smaller interfaces with fewer methods each related to a specific functionality. 

5. Dependency Inversion Principle (DIP): High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details. Details (concrete implementations) should depend on abstractions. This principle promotes loose coupling and makes code more flexible and maintainable. 

## React JS (TS) components
1. Component-Based Architecture:
- Small, Focused Components: Create small, reusable components with a single responsibility. This enhances reusability and makes the codebase easier to understand and test.
- Functional Components & Hooks: Favor functional components with React Hooks for state management and side effects, as they promote cleaner, more concise code compared to class components.
- Component Composition: Build complex UIs by composing smaller, independent components, fostering a modular and scalable structure.

2. State Management:
- Minimize Stateful Components: Reduce the number of components that manage their own state, centralizing state management where appropriate (e.g., using Context API or state management libraries like Redux).
- Props for Data Flow: Pass data down the component tree using props, ensuring a clear and predictable data flow.

3. Code Organization & Readability:
- Clear Folder Structure: Establish a well-defined and consistent folder structure to organize components, styles, utilities, and other assets.
- Naming Conventions: Adhere to consistent naming conventions for components, variables, and functions for improved readability and collaboration.
- DRY Principle (Don't Repeat Yourself): Avoid code duplication by creating reusable logic and components, often achieved through custom hooks or helper functions.

4. Performance Optimization:
- Memoization: Utilize React.memo, useMemo, and useCallback to prevent unnecessary re-renders of components and optimize expensive computations.
- Code Splitting & Lazy Loading: Implement code splitting and lazy loading (using React.lazy and Suspense) to reduce initial bundle size and improve loading times.
- Proper Key Usage: When rendering lists, use stable and unique key props to help React efficiently identify and re-render list items.

5. Maintainability & Robustness:
- Error Boundaries: Implement error boundaries to gracefully handle errors within the component tree and prevent the entire application from crashing.
- Accessibility: Design and develop with accessibility in mind, ensuring the application is usable by individuals with disabilities.
- Testing: Write comprehensive unit and integration tests for components and logic to ensure correctness and prevent regressions.

## Desing principles for FastAPI
1. Modularity and Separation of Concerns:
Break down your application into smaller, manageable modules, each responsible for a specific task or functionality. This promotes code reusability and easier maintenance. For instance, separate routes, models, and business logic into distinct modules. 

2. SOLID principles

3. Dependency Injection:
Decouple components by injecting dependencies rather than creating them directly. This makes your code more flexible and easier to test. FastAPI provides built-in dependency injection through the Depends function. 

4. Testability:
Design your code with testability in mind. Use dependency injection and mocking to make your code easier to test with unit and integration tests. 

5. Pydantic for Data Validation:
Leverage Pydantic models for data validation, serialization, and deserialization. This ensures data integrity and provides automatic documentation. 

6. OpenAPI and Documentation:
FastAPI automatically generates OpenAPI (Swagger) and ReDoc documentation, making your API easy to understand and use. 

7. ASGI Servers:
Use a production-ready ASGI server like Gunicorn or Hypercorn for deploying your FastAPI application. 

8. Project Structure:
Organize your project into logical folders for routes, models, business logic, etc. This promotes code clarity and maintainability. 

9. Design Patterns:
Consider using design patterns like the Factory pattern to create objects in a flexible way, or the Singleton pattern to ensure a single instance of a class. 

# Task 1
Convert the template.html file into a proper frontend React TS app.

# Task 1
Finish task 1 first.

# Additional Context
We're building a rapid prototype of a systems engineering security and threat modeling design and analysis app.  

Ask questions before you start coding. 
Do not start coding until I'm confident you understand the goal.