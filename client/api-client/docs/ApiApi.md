# ApiApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**apiRegisterCreate**](ApiApi.md#apiregistercreate) | **POST** /api/register/ | Register |
| [**apiTimeRead**](ApiApi.md#apitimeread) | **GET** /api/time/ | Read Current Time |
| [**apiTokenCreate**](ApiApi.md#apitokencreate) | **POST** /api/token/ | Obtain Token |
| [**apiTokenRefreshCreate**](ApiApi.md#apitokenrefreshcreate) | **POST** /api/token/refresh/ | Refresh Token |
| [**obtainTokenAsDemoApiTokenAsDemoPost**](ApiApi.md#obtaintokenasdemoapitokenasdemopost) | **POST** /api/token/as-demo | Obtain Token As Demo |



## apiRegisterCreate

> TokenPair apiRegisterCreate(userRegister)

Register

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiRegisterCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new ApiApi();

  const body = {
    // UserRegister
    userRegister: ...,
  } satisfies ApiRegisterCreateRequest;

  try {
    const data = await api.apiRegisterCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **userRegister** | [UserRegister](UserRegister.md) |  | |

### Return type

[**TokenPair**](TokenPair.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTimeRead

> CurrentTime apiTimeRead()

Read Current Time

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTimeReadRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new ApiApi();

  try {
    const data = await api.apiTimeRead();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**CurrentTime**](CurrentTime.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTokenCreate

> TokenPair apiTokenCreate(tokenObtainPair)

Obtain Token

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTokenCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new ApiApi();

  const body = {
    // TokenObtainPair
    tokenObtainPair: ...,
  } satisfies ApiTokenCreateRequest;

  try {
    const data = await api.apiTokenCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **tokenObtainPair** | [TokenObtainPair](TokenObtainPair.md) |  | |

### Return type

[**TokenPair**](TokenPair.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTokenRefreshCreate

> AccessToken apiTokenRefreshCreate(tokenRefresh)

Refresh Token

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTokenRefreshCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new ApiApi();

  const body = {
    // TokenRefresh
    tokenRefresh: ...,
  } satisfies ApiTokenRefreshCreateRequest;

  try {
    const data = await api.apiTokenRefreshCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **tokenRefresh** | [TokenRefresh](TokenRefresh.md) |  | |

### Return type

[**AccessToken**](AccessToken.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## obtainTokenAsDemoApiTokenAsDemoPost

> TokenPair obtainTokenAsDemoApiTokenAsDemoPost()

Obtain Token As Demo

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ObtainTokenAsDemoApiTokenAsDemoPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new ApiApi();

  try {
    const data = await api.obtainTokenAsDemoApiTokenAsDemoPost();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**TokenPair**](TokenPair.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

