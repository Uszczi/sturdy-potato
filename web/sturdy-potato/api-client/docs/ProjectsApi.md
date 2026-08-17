# ProjectsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**projectsCreateCreate**](ProjectsApi.md#projectscreatecreate) | **POST** /projects/create/ |  |
| [**projectsRetrieve**](ProjectsApi.md#projectsretrieve) | **GET** /projects/ |  |
| [**projectsRetrieve2**](ProjectsApi.md#projectsretrieve2) | **GET** /projects/{id}/ |  |



## projectsCreateCreate

> string projectsCreateCreate(projectCreateInput)



### Example

```ts
import {
  Configuration,
  ProjectsApi,
} from '';
import type { ProjectsCreateCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: jwtAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ProjectsApi(config);

  const body = {
    // ProjectCreateInput (optional)
    projectCreateInput: ...,
  } satisfies ProjectsCreateCreateRequest;

  try {
    const data = await api.projectsCreateCreate(body);
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
| **projectCreateInput** | [ProjectCreateInput](ProjectCreateInput.md) |  | [Optional] |

### Return type

**string**

### Authorization

[cookieAuth](../README.md#cookieAuth), [jwtAuth](../README.md#jwtAuth)

### HTTP request headers

- **Content-Type**: `application/json`, `application/x-www-form-urlencoded`, `multipart/form-data`
- **Accept**: `text/html`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## projectsRetrieve

> string projectsRetrieve()



### Example

```ts
import {
  Configuration,
  ProjectsApi,
} from '';
import type { ProjectsRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: jwtAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ProjectsApi(config);

  try {
    const data = await api.projectsRetrieve();
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

**string**

### Authorization

[cookieAuth](../README.md#cookieAuth), [jwtAuth](../README.md#jwtAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `text/html`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## projectsRetrieve2

> string projectsRetrieve2(id)



### Example

```ts
import {
  Configuration,
  ProjectsApi,
} from '';
import type { ProjectsRetrieve2Request } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: jwtAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ProjectsApi(config);

  const body = {
    // number
    id: 56,
  } satisfies ProjectsRetrieve2Request;

  try {
    const data = await api.projectsRetrieve2(body);
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
| **id** | `number` |  | [Defaults to `undefined`] |

### Return type

**string**

### Authorization

[cookieAuth](../README.md#cookieAuth), [jwtAuth](../README.md#jwtAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `text/html`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

