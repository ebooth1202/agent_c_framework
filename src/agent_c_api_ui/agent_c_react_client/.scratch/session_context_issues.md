The current SessionContext It a giant monolith that's used in many places and needs broken up into multiple contexts with proper speration.  HOWEVER because it is such a convoluted mess we have already tried and failed once to tackle this. Our major failures last time were:

1. Failure to identify the many ways the context get's used and updated
    - We missed several API calls that happen as a result of UI changes updating the context, such as well the model name changes in the drop down and controls are made visible.
2. Lack of decent debug information to detect when things weent wrong.
3. Followed by MASSIVELY over ambitious debug tool efforts that destablized everything.
4. Intriduced race contditions in context intilaization.

This time around we need to:
1. Perform an in-depth analys of how the context is currently used, what actions get triggered by updates,
    - These areaea nees spelled out cleared so that I can have the original author verifty that we've nor missed anything
2. Develop a plan to refactor the session context in gradual steps
   - Each step MUST include a user verification step with testing insturctions for the user.
3. Determine any packages that the user should install to assist in this effort and erport them to the user.

Once we've comepleted this 
