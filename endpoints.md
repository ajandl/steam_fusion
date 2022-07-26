- [Pages](#pages)
  - [User Creation](#user-creation)
  - [User Login](#user-login)
  - [User info](#user-info)
  - [Other users](#other-users)
  - [Compared lists](#compared-lists)
- [Endpoints](#endpoints)
  - [/register](#register)
  - [/login](#login)
  - [/logout](#logout)
  - [Update user info](#update-user-info)
  - [Link SteamID](#link-steamid)
  - [Return list to display](#return-list-to-display)


# Pages

## User Creation
## User Login
## User info
## Other users
## Compared lists

<br>

# Endpoints

## /register
- POST
- Request: JSON with username, password, email
- Response:
  - 200: JSON with msg and username
  - 403: JSON with msg
  - 409: JSON with msg "Conflicting user identity"
- Assumption:
  - Front end will ask for the password twice and will verify that entries match.
  
## /login
- POST
- Request: JSON with username and password
- Response: 
  - 200: JSON with access_token
  - 401: JSON with msg

## /logout
- POST
- Response:
  - 200: JSON with msg

## Update user info
- POST
- Recieve userID, new username, new email address 

## Link SteamID
- POST
- Recieve userID, steam_handle

## Return list to display
- GET with query params: listID_1, listID_2

