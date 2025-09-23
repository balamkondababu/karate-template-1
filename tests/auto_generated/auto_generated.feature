Feature: Test Users API

  Background:
    * url 'https://example.com'

  Scenario: Get list of users
    Given path '/users'
    When method get
    Then status 200
    And match response == '#[]'

  Scenario: Create a new user
    Given path '/users'
    And request { name: '#string' }
    When method post
    Then status 201
    And match response == { id: '#number', name: '#string' }

  Scenario: Create a new user with invalid request body
    Given path '/users'
    And request {}
    When method post
    Then status 400

  Scenario: Get list of users with query parameters
    Given path '/users'
    And param limit = 10
    And param offset = 0
    When method get
    Then status 200
    And match response == '#[]'