# Manual Deployment Guide for Agentic AI Tutor

This guide provides the step-by-step instructions to manually configure and deploy the AI Tutor application on AWS.

## Part 1: Create the DynamoDB Table (The Memory)

1.  Navigate to the **DynamoDB** service in the AWS Console.
2.  Click **"Create table"**.
3.  **Table name:** AgenticTutorSessions (must match what we'll set later).
4.  **Partition key (PK):** PK, Type: String.
5.  **Sort key (SK):** SK, Type: String.
6.  Leave all other settings as default and click **"Create table"**.

## Part 2: Create the IAM Role (The Permissions)

1.  Navigate to the **IAM** service.
2.  Go to **"Roles"** and click **"Create role"**.
3.  **Trusted entity type:** Select **"AWS service"**.
4.  **Use case:** Select **"Lambda"**. Click **"Next"**.
5.  **Add permissions:**
    * Search for and add AWSLambdaBasicExecutionRole (for logs).
    * Search for and add AmazonDynamoDBFullAccess (for LangGraph memory).
    * (Optional) If using Bedrock, add AmazonBedrockFullAccess.
6.  **Name the role:** AgenticTutor-LambdaRole. Click **"Create role"**.

## Part 3: Create the Lambda Function (The Brain)

1.  Navigate to the **Lambda** service.
2.  Click **"Create function"**.
3.  **Function name:** AgenticTutorOrchestrator.
4.  **Runtime:** Python 3.11.
5.  **Permissions:** Expand "Change default execution role", select **"Use an existing role"**, and choose the AgenticTutor-LambdaRole you just created.
6.  Click **"Create function"**.

### 3a. Configure the Lambda

1.  On your new function's page, go to the **"Configuration"** tab, then **"General configuration"**, and click **"Edit"**.
2.  Set the **Timeout** to **1 minute**. Click **"Save"**.
3.  Go back to the **"Configuration"** tab, then **"Environment variables"**, and click **"Edit"**.
4.  Add two variables:
    * SESSIONS_TABLE_NAME: AgenticTutorSessions
    * OPENAI_API_KEY: sk-YourSecretKeyGoesHere
5.  Click **"Save"**.

### 3b. Upload the Code

1.  In your local project on your computer, navigate into the src folder.
2.  Create a zip file containing lambda_function.py and equirements.txt. **Important: Do not zip the src folder itself, but its contents.**
3.  Back in the Lambda console, on the **"Code"** tab, click the **"Upload from"** button and select **".zip file"**.
4.  Upload the zip file you just created.

## Part 4: Create the API Gateway (The Front Door)

1.  Navigate to the **API Gateway** service.
2.  Click **"Build"** on the **REST API** card.
3.  **API name:** AgenticTutorAPI. Click **"Create API"**.
4.  With / selected, click **"Actions" -> "Create Resource"**. Name it chat.
5.  With /chat selected, click **"Actions" -> "Create Method"**. Choose POST.
6.  **Integration type:** Lambda Function.
7.  **Use Lambda Proxy integration:** Check this box.
8.  **Lambda Function:** Select your AgenticTutorOrchestrator function. Click **"Save"**.

## Part 5: Create the User Pool & Secure the API

1.  Navigate to the **Cognito** service.
2.  Click **"Create user pool"**. Follow the wizard to create a new pool (standard defaults are fine). Note the **User pool ID**.
3.  Go back to **API Gateway -> AgenticTutorAPI**. In the left menu, click **"Authorizers"**.
4.  Click **"Create authorizer"**:
    * **Name:** CognitoAuthorizer.
    * **Type:** Cognito.
    * **Cognito User Pool:** Select your new user pool.
    * **Token Source:** Authorization (this is the header name).
5.  Go to **Resources -> /chat -> POST**. Click **"Method Request"**.
6.  **Authorization:** Change from NONE to your new CognitoAuthorizer.
7.  Finally, click **"Actions" -> "Deploy API"**. Deploy to a new stage named 1.

Your application is now live and secure.
