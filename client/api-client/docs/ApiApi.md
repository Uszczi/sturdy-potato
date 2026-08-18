# ApiApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**apiProjectsCreate**](ApiApi.md#apiprojectscreate) | **POST** /api/projects/ | Create Project |
| [**apiProjectsDestroy**](ApiApi.md#apiprojectsdestroy) | **DELETE** /api/projects/{id}/ | Delete Project |
| [**apiProjectsList**](ApiApi.md#apiprojectslist) | **GET** /api/projects/ | List Projects |
| [**apiProjectsPartialUpdate**](ApiApi.md#apiprojectspartialupdate) | **PATCH** /api/projects/{id}/ | Update Project |
| [**apiProjectsReorderCreate**](ApiApi.md#apiprojectsreordercreate) | **POST** /api/projects/reorder/ | Reorder Projects |
| [**apiProjectsRetrieve**](ApiApi.md#apiprojectsretrieve) | **GET** /api/projects/{id}/ | Retrieve Project |
| [**apiTasksCountRetrieve**](ApiApi.md#apitaskscountretrieve) | **GET** /api/tasks/count/ | Count Tasks |
| [**apiTasksCreate**](ApiApi.md#apitaskscreate) | **POST** /api/tasks/ | Create Task |
| [**apiTasksDestroy**](ApiApi.md#apitasksdestroy) | **DELETE** /api/tasks/{id}/ | Delete Task |
| [**apiTasksList**](ApiApi.md#apitaskslist) | **GET** /api/tasks/ | List Tasks |
| [**apiTasksOpenList**](ApiApi.md#apitasksopenlist) | **GET** /api/tasks/open/ | Open Tasks |
| [**apiTasksPartialUpdate**](ApiApi.md#apitaskspartialupdate) | **PATCH** /api/tasks/{id}/ | Update Task |
| [**apiTasksReorderCreate**](ApiApi.md#apitasksreordercreate) | **POST** /api/tasks/reorder/ | Reorder Tasks |
| [**apiTasksRetrieve**](ApiApi.md#apitasksretrieve) | **GET** /api/tasks/{id}/ | Retrieve Task |
| [**apiTasksViewList**](ApiApi.md#apitasksviewlist) | **GET** /api/tasks/view/ | View Tasks |
| [**apiTokenCreate**](ApiApi.md#apitokencreate) | **POST** /api/token/ | Obtain Token |
| [**apiTokenRefreshCreate**](ApiApi.md#apitokenrefreshcreate) | **POST** /api/token/refresh/ | Refresh Token |



## apiProjectsCreate

> ProjectSchema apiProjectsCreate(projectCreateInput)

Create Project

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiProjectsCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ApiApi(config);

  const body = {
    // ProjectCreateInput
    projectCreateInput: ...,
  } satisfies ApiProjectsCreateRequest;

  try {
    const data = await api.apiProjectsCreate(body);
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
| **projectCreateInput** | [ProjectCreateInput](ProjectCreateInput.md) |  | |

### Return type

[**ProjectSchema**](ProjectSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiProjectsDestroy

> apiProjectsDestroy(id)

Delete Project

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiProjectsDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ApiApi(config);

  const body = {
    // number
    id: 56,
  } satisfies ApiProjectsDestroyRequest;

  try {
    const data = await api.apiProjectsDestroy(body);
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

`void` (Empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiProjectsList

> Array&lt;ProjectSchema&gt; apiProjectsList()

List Projects

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiProjectsListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ApiApi(config);

  try {
    const data = await api.apiProjectsList();
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

[**Array&lt;ProjectSchema&gt;**](ProjectSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiProjectsPartialUpdate

> ProjectSchema apiProjectsPartialUpdate(id, projectUpdateInput)

Update Project

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiProjectsPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ApiApi(config);

  const body = {
    // number
    id: 56,
    // ProjectUpdateInput
    projectUpdateInput: ...,
  } satisfies ApiProjectsPartialUpdateRequest;

  try {
    const data = await api.apiProjectsPartialUpdate(body);
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
| **projectUpdateInput** | [ProjectUpdateInput](ProjectUpdateInput.md) |  | |

### Return type

[**ProjectSchema**](ProjectSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiProjectsReorderCreate

> apiProjectsReorderCreate(reorderInput)

Reorder Projects

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiProjectsReorderCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ApiApi(config);

  const body = {
    // ReorderInput
    reorderInput: ...,
  } satisfies ApiProjectsReorderCreateRequest;

  try {
    const data = await api.apiProjectsReorderCreate(body);
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
| **reorderInput** | [ReorderInput](ReorderInput.md) |  | |

### Return type

`void` (Empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiProjectsRetrieve

> ProjectSchema apiProjectsRetrieve(id)

Retrieve Project

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiProjectsRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ApiApi(config);

  const body = {
    // number
    id: 56,
  } satisfies ApiProjectsRetrieveRequest;

  try {
    const data = await api.apiProjectsRetrieve(body);
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

[**ProjectSchema**](ProjectSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTasksCountRetrieve

> TaskCountSchema apiTasksCountRetrieve(completed)

Count Tasks

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTasksCountRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ApiApi(config);

  const body = {
    // boolean (optional)
    completed: true,
  } satisfies ApiTasksCountRetrieveRequest;

  try {
    const data = await api.apiTasksCountRetrieve(body);
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
| **completed** | `boolean` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**TaskCountSchema**](TaskCountSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTasksCreate

> TodoSchema apiTasksCreate(todoCreateInput)

Create Task

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTasksCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ApiApi(config);

  const body = {
    // TodoCreateInput
    todoCreateInput: ...,
  } satisfies ApiTasksCreateRequest;

  try {
    const data = await api.apiTasksCreate(body);
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
| **todoCreateInput** | [TodoCreateInput](TodoCreateInput.md) |  | |

### Return type

[**TodoSchema**](TodoSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTasksDestroy

> apiTasksDestroy(id)

Delete Task

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTasksDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ApiApi(config);

  const body = {
    // number
    id: 56,
  } satisfies ApiTasksDestroyRequest;

  try {
    const data = await api.apiTasksDestroy(body);
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

`void` (Empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTasksList

> Array&lt;TodoSchema&gt; apiTasksList()

List Tasks

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTasksListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ApiApi(config);

  try {
    const data = await api.apiTasksList();
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

[**Array&lt;TodoSchema&gt;**](TodoSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTasksOpenList

> Array&lt;TodoSchema&gt; apiTasksOpenList(limit)

Open Tasks

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTasksOpenListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ApiApi(config);

  const body = {
    // number (optional)
    limit: 56,
  } satisfies ApiTasksOpenListRequest;

  try {
    const data = await api.apiTasksOpenList(body);
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
| **limit** | `number` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;TodoSchema&gt;**](TodoSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTasksPartialUpdate

> TodoSchema apiTasksPartialUpdate(id, todoUpdateInput)

Update Task

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTasksPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ApiApi(config);

  const body = {
    // number
    id: 56,
    // TodoUpdateInput
    todoUpdateInput: ...,
  } satisfies ApiTasksPartialUpdateRequest;

  try {
    const data = await api.apiTasksPartialUpdate(body);
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
| **todoUpdateInput** | [TodoUpdateInput](TodoUpdateInput.md) |  | |

### Return type

[**TodoSchema**](TodoSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTasksReorderCreate

> apiTasksReorderCreate(reorderInput)

Reorder Tasks

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTasksReorderCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ApiApi(config);

  const body = {
    // ReorderInput
    reorderInput: ...,
  } satisfies ApiTasksReorderCreateRequest;

  try {
    const data = await api.apiTasksReorderCreate(body);
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
| **reorderInput** | [ReorderInput](ReorderInput.md) |  | |

### Return type

`void` (Empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTasksRetrieve

> TodoSchema apiTasksRetrieve(id)

Retrieve Task

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTasksRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ApiApi(config);

  const body = {
    // number
    id: 56,
  } satisfies ApiTasksRetrieveRequest;

  try {
    const data = await api.apiTasksRetrieve(body);
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

[**TodoSchema**](TodoSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTasksViewList

> Array&lt;TodoSchema&gt; apiTasksViewList(view, project)

View Tasks

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTasksViewListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ApiApi(config);

  const body = {
    // string (optional)
    view: view_example,
    // number (optional)
    project: 56,
  } satisfies ApiTasksViewListRequest;

  try {
    const data = await api.apiTasksViewList(body);
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
| **view** | `string` |  | [Optional] [Defaults to `&#39;inbox&#39;`] |
| **project** | `number` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;TodoSchema&gt;**](TodoSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

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

