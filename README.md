# EDUGraphAPI - Office 365 Education Code Sample#

In this sample, we show you how to integrate with school roles/roster data as well as O365 services available via the Graph API. 

School data is kept in sync in O365 Education tenants by [Microsoft School Data Sync](http://sds.microsoft.com).  

**Table of contents**

- [Sample Goals](#sample-goals)
- [Prerequisites](#prerequisites)
- [Register the application in Azure Active Directory](#register-the-application-in-azure-active-directory)
- [Build and debug locally](#build-and-debug-locally)
- [Deploy the sample to Azure](#deploy-the-sample-to-azure)
- [Understand the code](#understand-the-code)
- [Questions and comments](#questions-and-comments)
- [Contributing](#contributing)

## Sample Goals

The sample demonstrates:

- Calling Graph APIs, including:

  - [Microsoft Azure Active Directory Graph API](https://www.nuget.org/packages/Microsoft.Azure.ActiveDirectory.GraphClient/)
  - [Microsoft Graph API](https://www.nuget.org/packages/Microsoft.Graph/)

- Linking locally-managed user accounts and Office 365 (Azure Active Directory) user accounts. 

  After linking accounts, users can use either local or Office 365 accounts to log into the sample website and use it.

- Getting schools, sections, teachers, and students from Office 365 Education:

  - [Office 365 Schools REST API reference](https://msdn.microsoft.com/office/office365/api/school-rest-operations)

EDUGraphAPI is based on NodeJS (the server side) and Angular 2 (the client side).

## Prerequisites

**Deploying and running this sample requires**:

- An Azure subscription with permissions to register a new application, and deploy the web app.

- An O365 Education tenant with Microsoft School Data Sync enabled

  - One of the following browsers: Edge, Internet Explorer 9, Safari 5.0.6, Firefox 5, Chrome 13, or a later version of one of these browsers.

  Additionally: Developing/running this sample locally requires the following:  

  - [Python](https://www.python.org/downloads/) 3.5.2 or above
  - [Django](https://www.djangoproject.com/download/) 1.11 or above
  - [SQLite](https://www.sqlite.org/)

**Optional configuration**:

A feature in this sample demonstrates calling the Bing Maps API which requires a key to enable the Bing Maps feature. 

Create a key to enable Bing Maps API features in the app:

1. Open [https://www.bingmapsportal.com/](https://www.bingmapsportal.com/) in your web browser and sign in.

2. Click  **My account** -> **My keys**.

3. Create a **Basic** key, select **Public website** as the application type.

4. Copy the **Key** and save it. 

   ![](Images/bing-maps-key.png)

   > **Note:** The key is used in the app configuration steps for debug and deploy.


## Register the application in Azure Active Directory

1. Sign into the new azure portal: [https://portal.azure.com/](https://portal.azure.com/).

2. Choose your Azure AD tenant by selecting your account in the top right corner of the page:

   ![](Images/aad-select-directory.png)

3. Click **Azure Active Directory** -> **App registrations** -> **+Add**.

   ![](Images/aad-create-app-01.png)

4. Input a **Name**, and select **Web app / API** as **Application Type**.

   Input **Sign-on URL**: http://127.0.0.1:8000/

   ![](Images/aad-create-app-02.png)

   Click **Create**.

5. Once completed, the app will show in the list.

   ![](/Images/aad-create-app-03.png)

6. Click it to view its details. 

   ![](/Images/aad-create-app-04.png)

7. Click **All settings**, if the setting window did not show.

   - Click **Properties**, then set **Multi-tenanted** to **Yes**.

     ![](/Images/aad-create-app-05.png)

     Copy aside **Application ID**, then Click **Save**.

   - Click **Required permissions**. Add the following permissions:

     | API                            | Application Permissions | Delegated Permissions                    |
     | ------------------------------ | ----------------------- | ---------------------------------------- |
     | Microsoft Graph                |                         | Read all users' full profiles<br>Read all groups<br>Read directory data<br>Access directory as the signed in user<br>Sign users in |
     | Windows Azure Active Directory |                         | Sign in and read user profile<br>Read and write directory data |

     ![](/Images/aad-create-app-06.png)

   - Click **Keys**, then add a new key:

     ![](Images/aad-create-app-07.png)

     Click **Save**, then copy aside the **VALUE** of the key. 

   Close the Settings window.

## Build and debug locally

The following software arerequired:

- [Python](https://www.python.org/downloads/) 3.5.2 or above
- [Django](https://www.djangoproject.com/download/) 1.11 or above
- [SQLite](https://www.sqlite.org/)](https://git-scm.com/download/win)

Debug the app:

1. Configure the following **Environment Variables**:

   - **clientId**: use the Client Id of the app registration you created earlier.
   - **clientSecret**: use the Key value of the app registration you created earlier.
   - **BingMapKey**: use the key of Bing Map you got earlier. This setting is optional.
   - **SourceCodeRepositoryURL**: use the repository URL of your fork.

2. Open terminal and navigate to the source code folder. Execute the command below:

   ```sh
   pip install -r requirements.txt
   python manage.py runserver
   ```

3. Open http://127.0.0.1:8000/ in a browser.

## Deploy the sample to Azure

**GitHub Authorization**

1. Generate Token

   - Open https://github.com/settings/tokens in your web browser.
   - Sign into your GitHub account where you forked this repository.
   - Click **Generate Token**
   - Enter a value in the **Token description** text box
   - Select the followings (your selections should match the screenshot below):
     - repo (all) -> repo:status, repo_deployment, public_repo
     - admin:repo_hook -> read:repo_hook

   ![](Images/github-new-personal-access-token.png)

   - Click **Generate token**
   - Copy the token

2. Add the GitHub Token to Azure in the Azure Resource Explorer

   - Open https://resources.azure.com/providers/Microsoft.Web/sourcecontrols/GitHub in your web browser.
   - Log in with your Azure account.
   - Selected the correct Azure subscription.
   - Select **Read/Write** mode.
   - Click **Edit**.
   - Paste the token into the **token parameter**.

   ![](Images/update-github-token-in-azure-resource-explorer.png)

   - Click **PUT**

**Deploy the Azure Components from GitHub**

1. Check to ensure that the build is passing VSTS Build.

2. Fork this repository to your GitHub account.

3. Click the Deploy to Azure Button:

   [![Deploy to Azure](http://azuredeploy.net/deploybutton.png)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FTylerLu%2FEDUGraphAPI-Python%2Fmaster%2Fazuredeploy.json)

4. Fill in the values in the deployment page and select the **I agree to the terms and conditions stated above** checkbox.

   ![](Images/azure-auto-deploy.png)

   - **Resource group**: we suggest you create a new group.

   - **Site Name**: please input a name. Like EDUGraphAPICanviz or EDUGraphAPI993.

     > Note: If the name you input is taken, you will get some validation errors:
     >
     > ![](Images/azure-auto-deploy-validation-errors-01.png)
     >
     > Click it you will get more details like storage account is already in other resource group/subscription.
     >
     > In this case, please use another name.

   - **Source Code Repository URL**: replace <YOUR REPOSITORY> with the repository name of your fork.

   - **Source Code Manual Integration**: choose **false**, since you are deploying from your own fork.

   - **Client Id**: use the Client Id of the app registration you created earlier.

   - **Client Secret**: use the Key value of the app registration you created earlier.

   - **Bing Map Key**: use the key of Bing Map you got earlier. This setting is optional. It will hide Bing map icon on schools page if this field is empty.

   - Check **I agree to the terms and conditions stated above**.

5. Click **Purchase**.

**Add REPLY URL to the app registration**

1. After the deployment, open the resource group:

   ![](Images/azure-resource-group.png)

2. Click the web app.

   ![](Images/azure-web-app.png)

   Copy the URL aside and change the schema to **https**. This is the replay URL and will be used in next step.

3. Navigate to the app registration in the new azure portal, then open the setting windows.

   Add the reply URL:

   ![](Images/aad-add-reply-url.png)

   > Note: to debug the sample locally, make sure that http://127.0.0.1:8000/ is in the reply URLs.

4. Click **SAVE**.

## Understand the code

### Introduction

**Solution Component Diagram**

![](Images/solution-component-diagram.png)

The top layer of the solution contains the two parts of the EDUGraphAPI.Web project:

* The server side Node.js app.
* The client side Angular 2 app.

The bottom layers contain the three data sources.

* The EDUGraphAPI database.
* Education data exposed by REST APIs.
* Azure AD data exposed by Graph APIs.

### **EDUGraphAPI.Web - Server**

The server side app is based on Node.js and implemented with Typescript.

**Authentication Mechanisms**

Passport and its 2 plugins are used to enable local and O365 authentications:

* **[passport-azure-ad](https://github.com/AzureAD/passport-azure-ad)**: a collection of [Passport](http://passportjs.org/) Strategies to help you integrate with Azure Active Directory. It includes OpenID Connect, WS-Federation, and SAML-P authentication and authorization. These providers let you integrate your Node app with Microsoft Azure AD so you can use its many features, including web single sign-on (WebSSO), Endpoint Protection with OAuth, and JWT token issuance and validation.
* **[passport-local](https://github.com/jaredhanson/passport-local)**: this module lets you authenticate using a username and password in your Node.js applications. By plugging into Passport, local authentication can be easily and unobtrusively integrated into any application or framework that supports [Connect](http://www.senchalabs.org/connect/)-style middleware, including [Express](http://expressjs.com/).

The 2 kinds of authentication are implemented in the **/auth/appAuth.ts** file.

**Web APIs**

The server app exposes several Web APIs:

| Path                                     | Method   | Description                              |
| ---------------------------------------- | -------- | ---------------------------------------- |
| /api/me                                  | GET      | Return the current user and the user's organization and roles |
| /api/me/favoriteColor                    | POST     | Update current user's favorite color     |
| /api/me/accesstoken                      | GET      | Get current user's access token          |
| /api/tenant                              | POST     | Update information (isAdminConsented) of current user's tenant |
| /api/tenant/unlinkAllUsers               | POST     | Unlink all users in current user's tenant |
| /api/users/linked                        | GET      | Get all linked users                     |
| /api/users/:userId/unlink                | POST     | Unlink the specified user                |
| /api/admin/consent                       | GET      | Redirect the user to login page to perform admin consent |
| /api/admin/consented                     | POST     | Will be invoked after admin consented    |
| /api/schools/seatingArrangements/:classId | GET/POST | Get or set the seating arrangement of the specified class |

These APIs are defined in the **/routes** folder.

**Data Access**

[Sequelize](http://docs.sequelizejs.com/en/v3/) is used in this sample to access data from a SQL Database. 

The **DbContext** exposes the models and methods that are used to access data.

The tables used in this demo:

| Table                        | Description                              |
| ---------------------------- | ---------------------------------------- |
| Users                        | Contains the user's information: name, email, hashed password...<br>*O365UserId* and *O365Email* are used to connect the local user with an O365 user. |
| UserRoles                    | Contains users' role. Three roles are used in this sample: admin, teacher, and student. |
| Organizations                | A row in this table represents a tenant in AAD.<br>*IsAdminConsented* column records than if the tenant consented by an administrator. |
| TokenCache                   | Contains the users' access/refresh tokens. |
| ClassroomSeatingArrangements | Contains the classroom seating arrangements. |

You will find the **DbContext** class and related model interfaces in the **/data/dbContext.ts** file.

**Services**

The services used by the server side app:

| Service           | Description                              |
| ----------------- | ---------------------------------------- |
| MSGraphClient     | Contains methods used to access MS Graph APIs |
| SchoolService     | Contains two methods: get/update seating arrangements |
| TenantService     | Contains methods that operate tenants in the database |
| TokenCacheService | Contains method used to get and update cache from the database |
| UserService       | Contains method used to manipulate users in the database |

The services are in the **/services** folder.

**Multi-tenant app**

This web application is a **multi-tenant app**. In the AAD, we enabled the option:

![](Images/app-is-multi-tenant.png)

Users from any Azure Active Directory tenant can access this app. Some permissions used by this app require an administrator of the tenant to consent before users can use the app. Otherwise, users will see this error:

![](Images/app-requires-admin-to-consent.png)

For more information, see [Build a multi-tenant SaaS web application using Azure AD & OpenID Connect](https://azure.microsoft.com/en-us/resources/samples/active-directory-dotnet-webapp-multitenant-openidconnect/).

### **EDUGraphAPI.Web - Client**

The client side app which resides in the /app folder is based on Angular 2 and is also implemented with Typescript 2.

> Note:  Getting and using declaration files in TypeScript 2.0 is much easier than in TypeScript 1. To get declarations for a library like lodash for example, all you need is npm:
>
> ```
> npm install --save @types/lodash
> ```

**Components**

These components are used in the client app.

| Folder      | Component             |
| ----------- | --------------------- |
| /           | App                   |
| /aboutme    | AboutMe               |
| /admin      | Admin                 |
|             | LinkedAccounts        |
|             | Consent               |
| /demoHeoper | DemoHelper            |
| /header     | Header                |
| /link       | Link                  |
|             | LinkCreateLocal       |
|             | LinkLoginLocal        |
|             | LinkLoginO365Requried |
| /login      | Login                 |
| /O365login  | O365login             |
| /register   | Register              |
| /schools    | Schools               |
|             | Classes               |
|             | MyClasses             |
|             | ClassDetails          |

**Services**

| Folder      | Name              |
| ----------- | ----------------- |
| /aboutme    | AboutMeService    |
| /admin      | AdminService      |
| /demoHelper | DemoHelperService |
| /link       | LinkService       |
| /services   | MeService         |
|             | UserService       |
|             | UserPhotoService  |
|             | DataService       |

### Office 365 Education API

The [Office 365 Education APIs](https://msdn.microsoft.com/office/office365/api/school-rest-operations) return data from any Office 365 tenant which has been synced to the cloud by Microsoft School Data Sync. The APIs provide information about schools, sections, teachers, students, and rosters. The Schools REST API provides access to school entities in Office 365 for Education tenants.

In this sample, the **Microsoft.Education** Class Library project encapsulates the Office 365 Education API. 

The **EducationServiceClient** is the core class of the library. It is used to easily get education data.

**Get schools**

~~~typescript
getSchools(): Observable<any[]> {
    return this.dataService.getArray<any>(this.urlBase + "/administrativeUnits?api-version=beta");
}
~~~

~~~typescript
getSchoolById(id: string): Observable<any> {
    return this.dataService.getObject(this.urlBase + '/administrativeUnits/' + id + '?api-version=beta');
}
~~~

**Get classes**

~~~typescript
getClasses(schoolId: string, nextLink: string): Observable<PagedCollection<any>> {
    let url: string = this.urlBase + "/groups?api-version=beta&$top=12&$filter=extension_fe2174665583431c953114ff7268b7b3_Education_ObjectType%20eq%20'Section'%20and%20extension_fe2174665583431c953114ff7268b7b3_Education_SyncSource_SchoolId%20eq%20'" + schoolId + "'" +
        (nextLink ? "&" + GraphHelper.getSkipToken(nextLink) : '');
    return this.dataService.getPagedCollection<any>(url);
}
~~~

```typescript
getClassById(classId: string): Observable<any> {
    return this.dataService.getObject<any>(this.urlBase + "/groups/" + classId + "?api-version=beta&$expand=members");
}
```
**Get users**

```typescript
getUsers(schoolId: string, nextLink: string): Observable<PagedCollection<any>> {
    var url = this.urlBase + "/administrativeUnits/" + schoolId + "/members?api-version=beta&$top=12" +
        (nextLink ? "&" + GraphHelper.getSkipToken(nextLink) : '');
    return this.dataService.getPagedCollection<any>(url);
}
```
Below are some screenshots of the sample app that show the education data.

![](Images/edu-schools.png)

![](Images/edu-users.png)

![](Images/edu-classes.png)

![](Images/edu-class.png)

In **/app/services/dataService.ts**, three generic methods simplify the invoking of REST APIs.

* **getObject<T>**: sends a http GET request to the target endpoint, and deserializes the JSON response string to T, and return the result object.  
* **getPagedCollection<T>**:  sends a http GET request to the target endpoint, and deserializes the JSON response string to PagedCollection<T>, and return the result object. 
* **getArray<T>**: sends a http GET request to the target endpoint, and deserializes the JSON response string to array, and return the array.

For http GET request sent by the 3 methods above, an access token is included in the bearer authentication header.

### Authentication Flows

There are 4 authentication flows in this project.

The first 2 flows (Local Login/O365 Login) enable users to login in with either a local account or an Office 365 account, then link to the other type account. This procedure is implemented in the LinkController.

**Local Login Authentication Flow**

![](Images/auth-flow-local-login.png)

**O365 Login Authentication Flow**

![](Images/auth-flow-o365-login.png)

**Admin Login Authentication Flow**

This flow shows how an administrator logs into the system and performs administrative operations.

After logging into the app with an office 365 account,the administrator will be asked to link to a local account. This step is not required and can be skipped. 

As mentioned earlier, the web app is a multi-tenant app which uses some application permissions, so tenant administrator must consent the app first.  

This flow is implemented in the AdminController. 

![](Images/auth-flow-admin-login.png)

### Two Kinds of Graph APIs

There are two distinct Graph APIs used in this sample:

|              | [Azure AD Graph API](https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-graph-api) | [Microsoft Graph API](https://graph.microsoft.io/) |
| ------------ | ---------------------------------------- | ---------------------------------------- |
| Description  | The Azure Active Directory Graph API provides programmatic access to Azure Active Directory through REST API endpoints. Apps can use the Azure AD Graph API to perform create, read, update, and delete (CRUD) operations on directory data and directory objects, such as users, groups, and organizational contacts | A unified API that also includes APIs from other Microsoft services like Outlook, OneDrive, OneNote, Planner, and Office Graph, all accessed through a single endpoint with a single access token. |
| Client       | Install-Package [Microsoft.Azure.ActiveDirectory.GraphClient](https://www.nuget.org/packages/Microsoft.Azure.ActiveDirectory.GraphClient/) | Install-Package [Microsoft.Graph](https://www.nuget.org/packages/Microsoft.Graph/) |
| End Point    | https://graph.windows.net                | https://graph.microsoft.com              |
| API Explorer | https://graphexplorer.cloudapp.net/      | https://graph.microsoft.io/graph-explorer |

> **IMPORTANT NOTE:** Microsoft is investing heavily in the new Microsoft Graph API, and they are not investing in the Azure AD Graph API anymore (except fixing security issues).

> Therefore, please use the new Microsoft Graph API as much as possible and minimize how much you use the Azure AD Graph API.

Below is a piece of code shows how to get "me" from the Microsoft Graph API.

```typescript
public getMe(): Promise<any> {
    return new Promise((resolve, reject) => {
        request
            .get(Constants.MSGraphResource + "/v1.0/me/?$select=id,givenName,surname,userPrincipalName,assignedLicenses")
            .set('Authorization', 'Bearer ' + this.accessToken)
            .end((err, res) => {
                if (err) { return reject(err) }
                resolve(res.body);
            })
    })
}
```

Note that in the AAD Application settings, permissions for each Graph API are configured separately:

![](Images/aad-create-app-06.png) 

## Questions and comments

- If you have any trouble running this sample, please [log an issue](https://github.com/OfficeDev/O365-EDU-AspNetMVC-Samples/issues).
- Questions about GraphAPI development in general should be posted to [Stack Overflow](http://stackoverflow.com/questions/tagged/office-addins). Make sure that your questions or comments are tagged with [ms-graph-api]. 

## Contributing

We encourage you to contribute to our samples. For guidelines on how to proceed, see [our contribution guide](/Contributing.md).

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.



**Copyright (c) 2017 Microsoft. All rights reserved.**