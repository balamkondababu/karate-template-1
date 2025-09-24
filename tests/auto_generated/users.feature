### karate-config.js Updates

To support the provided OpenAPI specification, we need to add the following test data variables to the existing `karate-config.js`:

```javascript
// Add these to your existing config object
testData: {
  validUserName: 'John Doe',
  validUserId: 1,
  invalidUserId: 999,
  validApplicationId: 1,
  invalidApplicationId: 999
}
```

### Feature Files

We will create separate feature files for each logical API grouping. In this case, we have two main groups: `user-management.feature` and `error-handling.feature`.

#### user-management.feature

```gherkin
Feature: User Management

Background:
  * url baseUrl
  * configure headers = { 'Content-Type': 'application/json' }
  * def testData = { 
    validUserName: '#(testData.validUserName)',
    validUserId: '#(testData.validUserId)',
    invalidUserId: '#(testData.invalidUserId)',
    validApplicationId: '#(testData.validApplicationId)',
    invalidApplicationId: '#(testData.invalidApplicationId)'
  }

Scenario: Get list of users
  Given path 'users'
  When method get
  Then status 200
  And match response == '#[]'

Scenario: Create a new user
  Given path 'users'
  And request { name: '#(testData.validUserName)' }
  When method post
  Then status 201
  And match response == { id: '#number', name: '#string' }

Scenario: Get user by ID
  Given path 'users', testData.validUserId
  When method get
  Then status 200
  And match response == { id: '#number', name: '#string' }

Scenario: Get user by ID with invalid ID
  Given path 'users', testData.invalidUserId
  When method get
  Then status 404

Scenario Outline: Get user by application ID
  Given path 'users', '<userId>', '<applicationId>'
  When method get
  Then status <statusCode>
  And match response == <response>

  Examples:
    | userId | applicationId | statusCode | response               |
    | 1      | 1             | 200        | { id: '#number', name: '#string' } |
    | 1      | 999           | 404        | { error: '#string' }             |
    | 999    | 1             | 404        | { error: '#string' }             |
```

#### error-handling.feature

```gherkin
Feature: Error Handling

Background:
  * url baseUrl
  * configure headers = { 'Content-Type': 'application/json' }
  * def testData = { 
    validUserName: '#(testData.validUserName)',
    validUserId: '#(testData.validUserId)',
    invalidUserId: '#(testData.invalidUserId)',
    validApplicationId: '#(testData.validApplicationId)',
    invalidApplicationId: '#(testData.invalidApplicationId)'
  }

Scenario: Get user by ID with invalid ID
  Given path 'users', testData.invalidUserId
  When method get
  Then status 404
  And match response == { error: '#string' }

Scenario: Get user by application ID with invalid application ID
  Given path 'users', testData.validUserId, testData.invalidApplicationId
  When method get
  Then status 404
  And match response == { error: '#string' }

Scenario: Get user by application ID with invalid user ID
  Given path 'users', testData.invalidUserId, testData.validApplicationId
  When method get
  Then status 404
  And match response == { error: '#string' }
```

### Execution Commands

To execute the tests, use the following commands:

* Single feature: `mvn test -Dkarate.options="classpath:user-management.feature"`
* Full suite: `mvn test -Dkarate.options="--tags ~@ignore"`
* With environment: `mvn test -Dkarate.env=test`

Note: Make sure to replace `baseUrl` with the actual base URL of your API.