"""
Day 6: Circuit Breaker Pattern

Protects distributed systems from cascading failures by monitoring and
controlling calls to potentially failing services.

Usage:
    python 10_02_2026_circuit_breaker_pattern.py
"""

# import: Keyword to bring external modules into current namespace
# time: Module providing time-related functions (time.time() for timestamps)
# Why: Need to track elapsed time for recovery timeout
import time

# logging: Module for tracking events and state transitions
# Why: Essential for debugging and monitoring circuit state changes
import logging

# functools: Module containing higher-order functions
# wraps: Decorator that preserves original function metadata
# Why: When using decorators, maintains function name, docstring, etc.
from functools import wraps

# enum: Module for creating enumerated constants
# Enum: Base class for creating enumerations
# Why: Type-safe way to represent circuit states (better than strings)
from enum import Enum

# Configure: Set up logging behavior
# basicConfig: Function to configure root logger
# level=logging.INFO: Show INFO level and above messages
# format: Template for log message appearance
# Why: Makes state transitions visible for debugging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


# class: Keyword to define a new class
# CircuitState: Name representing possible circuit states
# (Enum): Inherits from Enum base class
# Why: Enum prevents typos and provides type safety for states
class CircuitState(Enum):
    # CLOSED: Constant name for normal operation state
    # = "CLOSED": String value assigned to this state
    # Why: Normal state where requests pass through
    CLOSED = "CLOSED"
    
    # OPEN: Constant name for blocking state
    # = "OPEN": String value for blocked state
    # Why: Protective state that blocks all requests
    OPEN = "OPEN"
    
    # HALF_OPEN: Constant name for testing state
    # = "HALF_OPEN": String value for recovery testing
    # Why: Allows one test request to check if service recovered
    HALF_OPEN = "HALF_OPEN"


# class: Define custom exception class
# CircuitOpenError: Name for circuit-specific exception
# (Exception): Inherits from base Exception class
# Why: Distinguishes circuit blocks from actual service failures
class CircuitOpenError(Exception):
    """Raised when the circuit is open"""
    # pass: No additional implementation needed
    # Why: Inheriting from Exception provides all needed functionality
    pass


# class: Define the main circuit breaker class
# CircuitBreaker: Name of the class
# Why: Encapsulates all circuit breaker logic and state
class CircuitBreaker:
    # def: Define a method
    # __init__: Special method called when creating instance
    # self: Reference to the instance being created
    # failure_threshold: Parameter - number of failures before opening
    # int: Type hint indicating integer expected
    # = 3: Default value if not provided
    # recovery_timeout: Parameter - seconds to wait before testing
    # = 5: Default 5 seconds recovery time
    # Why: Constructor initializes circuit breaker with configurable thresholds
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 5):
        # self.failure_threshold: Instance variable storing threshold
        # = failure_threshold: Assign parameter value to instance
        # Why: Store threshold for later comparison with failure count
        self.failure_threshold = failure_threshold
        
        # self.recovery_timeout: Instance variable for timeout duration
        # = recovery_timeout: Assign parameter value
        # Why: Store how long to wait before attempting recovery
        self.recovery_timeout = recovery_timeout
        
        # self.state: Instance variable tracking current state
        # = CircuitState.CLOSED: Start in normal operation state
        # Why: Circuit begins in healthy state, assumes service is working
        self.state = CircuitState.CLOSED
        
        # self.failures: Instance variable counting consecutive failures
        # = 0: Initialize to zero failures
        # Why: Track failures to compare against threshold
        self.failures = 0
        
        # self.last_failure_time: Instance variable storing timestamp
        # = 0: Initialize to zero (no failures yet)
        # Why: Track when last failure occurred for timeout calculation
        self.last_failure_time = 0

    # def: Define method
    # __call__: Special method making instance callable like a function
    # self: Reference to circuit breaker instance
    # func: Parameter - the function to be decorated
    # Why: Allows CircuitBreaker to be used as @decorator syntax
    def __call__(self, func):
        """Allows the class to be used as a decorator."""
        
        # @wraps(func): Decorator preserving original function metadata
        # Why: Maintains func's __name__, __doc__, etc. after decoration
        @wraps(func)
        # def: Define inner wrapper function
        # wrapper: Name of the wrapping function
        # *args: Captures all positional arguments
        # **kwargs: Captures all keyword arguments
        # Why: Wrapper intercepts calls to add circuit breaker logic
        def wrapper(*args, **kwargs):
            # self._update_state(): Call method to check state transitions
            # Why: Before each call, check if timeout elapsed (OPEN→HALF_OPEN)
            self._update_state()

            # if: Conditional check
            # self.state == CircuitState.OPEN: Compare current state
            # Why: Block requests when circuit is open (service is failing)
            if self.state == CircuitState.OPEN:
                # raise: Throw an exception
                # CircuitOpenError: Custom exception type
                # "Circuit is open": Error message
                # Why: Immediately fail without calling service
                raise CircuitOpenError("Circuit is open")
            
            # try: Begin exception handling block
            # Why: Catch failures to count them and update state
            try:
                # return: Exit function with value
                # func(*args, **kwargs): Call original function with arguments
                # Why: Execute the actual service call
                result = func(*args, **kwargs)
                
                # self._on_success(): Call success handler
                # Why: Reset failure count and potentially close circuit
                self._on_success()
                
                # return result: Return the successful result
                # Why: Pass through the service response
                return result
                
            # except: Catch exceptions
            # Exception as e: Catch any exception, store in variable e
            # Why: Any failure should be counted and handled
            except Exception as e:
                # self._on_failure(e): Call failure handler with exception
                # Why: Increment failure count and potentially open circuit
                self._on_failure(e)
                
                # raise e: Re-raise the exception
                # Why: Let caller know the request failed
                raise e
                
        # return wrapper: Return the wrapped function
        # Why: Decorator must return the new wrapped version
        return wrapper
    
    # def: Define method
    # _update_state: Method name (underscore = internal/private)
    # self: Reference to instance
    # Why: Encapsulates state transition logic from OPEN to HALF_OPEN
    def _update_state(self):
        """Internal logic to transition from OPEN to HALF_OPEN after timeout."""
        
        # if: Conditional check with multiple conditions
        # self.state == CircuitState.OPEN: Check if currently open
        # and: Logical operator requiring both conditions true
        # self.last_failure_time: Check if timestamp exists (not 0)
        # Why: Only check timeout if circuit is open and has failure time
        if self.state == CircuitState.OPEN and self.last_failure_time:
            # elapsed: Variable storing time difference
            # = time.time(): Get current timestamp in seconds
            # - self.last_failure_time: Subtract last failure timestamp
            # Why: Calculate how long circuit has been open
            elapsed = time.time() - self.last_failure_time
            
            # if: Check if enough time passed
            # elapsed >= self.recovery_timeout: Compare elapsed vs timeout
            # Why: Only attempt recovery after timeout period
            if elapsed >= self.recovery_timeout:
                # logging.info(): Log informational message
                # Why: Track state transition for debugging
                logging.info("--- Timeout reached. Transitioning to HALF_OPEN (Testing...) ---")
                
                # self.state = CircuitState.HALF_OPEN: Change state
                # Why: Allow one test request to check service health
                self.state = CircuitState.HALF_OPEN

    # def: Define method
    # _on_success: Method called when request succeeds
    # self: Instance reference
    # Why: Handle successful requests and state transitions
    def _on_success(self):
        """Logic to execute on a successful call."""
        
        # if: Check current state
        # self.state == CircuitState.HALF_OPEN: Testing state?
        # Why: Success in HALF_OPEN means service recovered
        if self.state == CircuitState.HALF_OPEN:
            # logging.info(): Log the recovery
            # Why: Important event - service is healthy again
            logging.info("--- Success! Transitioning to CLOSED ---")
        
        # self.state = CircuitState.CLOSED: Set to normal state
        # Why: Service is working, allow all requests
        self.state = CircuitState.CLOSED
        
        # self.failures = 0: Reset failure counter
        # Why: Success clears failure history
        self.failures = 0
        
        # self.last_failure_time = None: Clear failure timestamp
        # Why: No recent failures to track
        self.last_failure_time = None

    # def: Define method
    # _on_failure: Method called when request fails
    # self: Instance reference
    # error: Parameter containing the exception
    # Why: Handle failures and potentially open circuit
    def _on_failure(self, error):
        """Logic to execute on a failed call."""
        
        # self.failures += 1: Increment operator
        # Why: Count this failure toward threshold
        self.failures += 1
        
        # self.last_failure_time = time.time(): Store current timestamp
        # Why: Track when failure occurred for timeout calculation
        self.last_failure_time = time.time()
        
        # logging.warning(): Log warning level message
        # f"...": F-string for string interpolation
        # {self.failures}/{self.failure_threshold}: Show progress to threshold
        # Why: Track how close we are to opening circuit
        logging.warning(f"Failure {self.failures}/{self.failure_threshold}: {error}")
        
        # if: Check if should open circuit
        # self.state == CircuitState.HALF_OPEN: Test failed?
        # or: Logical operator - either condition triggers
        # self.failures >= self.failure_threshold: Reached limit?
        # Why: Open circuit if test fails OR threshold exceeded
        if self.state == CircuitState.HALF_OPEN or self.failures >= self.failure_threshold:
            # logging.error(): Log error level message
            # Why: Circuit opening is critical event
            logging.error("--- Threshold reached. Tripping circuit to OPEN. ---")
            
            # self.state = CircuitState.OPEN: Change to blocking state
            # Why: Protect system by blocking further requests
            self.state = CircuitState.OPEN


# --- Example Usage ---

# @CircuitBreaker: Decorator syntax
# (failure_threshold=3, recovery_timeout=5): Decorator arguments
# Why: Protect this function with circuit breaker logic
@CircuitBreaker(failure_threshold=3, recovery_timeout=5)
# def: Define function to be protected
# call_external_api: Function name
# should_fail: Parameter controlling behavior for testing
# =False: Default to success
# Why: Simulate an external API that can fail
def call_external_api(should_fail=False):
    # if: Check parameter
    # should_fail: Boolean parameter
    # Why: Allow testing both success and failure scenarios
    if should_fail:
        # raise: Throw exception
        # ConnectionError: Built-in exception for connection issues
        # Why: Simulate API being down
        raise ConnectionError("API is down")
    
    # return: Exit with value
    # "API Success": String indicating success
    # Why: Return successful response
    return "API Success"


# if: Check if script is main program
# __name__ == "__main__": True when run directly (not imported)
# Why: Only run demo when script executed directly
if __name__ == "__main__":
    # Phase 1: Trigger failures to OPEN the circuit
    print("--- Phase 1: Failing attempts ---")
    
    # for: Loop construct
    # _ in range(3): Iterate 3 times (underscore = unused variable)
    # Why: Generate 3 failures to reach threshold
    for _ in range(3):
        # try: Begin exception handling
        # Why: Catch expected failures
        try:
            # call_external_api(should_fail=True): Call with failure
            # Why: Simulate service being down
            call_external_api(should_fail=True)
        # except: Catch specific exception
        # CircuitOpenError as e: Catch circuit blocks
        # Why: Handle circuit opening gracefully
        except (CircuitOpenError, ConnectionError) as e:
            # logging.info(): Log the expected error
            # f"Caught expected error: {e}": Format error message
            # Why: Show that errors are being caught properly
            logging.info(f"Caught expected error: {e}")

    # Phase 2: Try calling while OPEN
    print("\n--- Phase 2: Calling while OPEN ---")
    # try: Attempt call
    # Why: Demonstrate circuit blocking requests
    try:
        # call_external_api(): Call without arguments (should_fail=False)
        # Why: Even healthy call should be blocked when OPEN
        call_external_api()
    # except: Catch circuit block
    # CircuitOpenError as e: Circuit is blocking
    # Why: Expected behavior when circuit is open
    except CircuitOpenError as e:
        # logging.info(): Log the block
        # Why: Show circuit is protecting the system
        logging.info(f"Caught expected error: {e}")

    # Phase 3: Wait for recovery
    print("\n--- Phase 3: Waiting for recovery timeout... ---")
    # time.sleep(6): Pause execution for 6 seconds
    # Why: Wait longer than recovery_timeout (5s) to trigger HALF_OPEN
    time.sleep(6)

    # Phase 4: Test the circuit (HALF_OPEN)
    print("--- Phase 4: Testing recovery ---")
    # print(): Output result
    # call_external_api(should_fail=False): Call with success
    # Why: Test request should succeed and close circuit
    print(call_external_api(should_fail=False))
