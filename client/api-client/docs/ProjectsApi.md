# ProjectsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**apiProjectsCreate**](ProjectsApi.md#apiprojectscreate) | **POST** /api/workspaces/{workspace_id}/projects/ | Create Project |
| [**apiProjectsDestroy**](ProjectsApi.md#apiprojectsdestroy) | **DELETE** /api/workspaces/{workspace_id}/projects/{id}/ | Delete Project |
| [**apiProjectsList**](ProjectsApi.md#apiprojectslist) | **GET** /api/workspaces/{workspace_id}/projects/ | List Projects |
| [**apiProjectsPartialUpdate**](ProjectsApi.md#apiprojectspartialupdate) | **PATCH** /api/workspaces/{workspace_id}/projects/{id}/ | Update Project |
| [**apiProjectsReorderCreate**](ProjectsApi.md#apiprojectsreordercreate) | **POST** /api/workspaces/{workspace_id}/projects/reorder/ | Reorder Projects |
| [**apiProjectsRetrieve**](ProjectsApi.md#apiprojectsretrieve) | **GET** /api/workspaces/{workspace_id}/projects/{id}/ | Retrieve Project |
| [**apiProjectsStatusesUpdate**](ProjectsApi.md#apiprojectsstatusesupdate) | **PUT** /api/workspaces/{workspace_id}/projects/{id}/statuses/ | Set Project Workflow |



## apiProjectsCreate

> ProjectSchema apiProjectsCreate(workspaceId, projectCreateInput)

Create Project

### Example

```ts
import {
  Configuration,
  ProjectsApi,
} from '';
import type { ApiProjectsCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ProjectsApi(config);

  const body = {
    // number
    workspaceId: 56,
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
| **workspaceId** | `number` |  | [Defaults to `undefined`] |
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

> apiProjectsDestroy(id, workspaceId)

Delete Project

### Example

```ts
import {
  Configuration,
  ProjectsApi,
} from '';
import type { ApiProjectsDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ProjectsApi(config);

  const body = {
    // number
    id: 56,
    // number
    workspaceId: 56,
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
| **workspaceId** | `number` |  | [Defaults to `undefined`] |

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

> Array&lt;ProjectSchema&gt; apiProjectsList(workspaceId)

List Projects

### Example

```ts
import {
  Configuration,
  ProjectsApi,
} from '';
import type { ApiProjectsListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ProjectsApi(config);

  const body = {
    // number
    workspaceId: 56,
  } satisfies ApiProjectsListRequest;

  try {
    const data = await api.apiProjectsList(body);
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
| **workspaceId** | `number` |  | [Defaults to `undefined`] |

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
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiProjectsPartialUpdate

> ProjectSchema apiProjectsPartialUpdate(id, workspaceId, projectUpdateInput)

Update Project

### Example

```ts
import {
  Configuration,
  ProjectsApi,
} from '';
import type { ApiProjectsPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ProjectsApi(config);

  const body = {
    // number
    id: 56,
    // number
    workspaceId: 56,
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
| **workspaceId** | `number` |  | [Defaults to `undefined`] |
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

> apiProjectsReorderCreate(workspaceId, reorderInput)

Reorder Projects

### Example

```ts
import {
  Configuration,
  ProjectsApi,
} from '';
import type { ApiProjectsReorderCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ProjectsApi(config);

  const body = {
    // number
    workspaceId: 56,
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
| **workspaceId** | `number` |  | [Defaults to `undefined`] |
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

> ProjectDetailSchema apiProjectsRetrieve(id, workspaceId)

Retrieve Project

### Example

```ts
import {
  Configuration,
  ProjectsApi,
} from '';
import type { ApiProjectsRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ProjectsApi(config);

  const body = {
    // number
    id: 56,
    // number
    workspaceId: 56,
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
| **workspaceId** | `number` |  | [Defaults to `undefined`] |

### Return type

[**ProjectDetailSchema**](ProjectDetailSchema.md)

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


## apiProjectsStatusesUpdate

> ProjectDetailSchema apiProjectsStatusesUpdate(id, workspaceId, workflowInput)

Set Project Workflow

Replace this project board\&#39;s workflow with the complete list sent.  One request covers adding, renaming, reordering and removing statuses, since the rules a workflow must satisfy only make sense against a finished list.

### Example

```ts
import {
  Configuration,
  ProjectsApi,
} from '';
import type { ApiProjectsStatusesUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ProjectsApi(config);

  const body = {
    // number
    id: 56,
    // number
    workspaceId: 56,
    // WorkflowInput
    workflowInput: ...,
  } satisfies ApiProjectsStatusesUpdateRequest;

  try {
    const data = await api.apiProjectsStatusesUpdate(body);
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
| **workspaceId** | `number` |  | [Defaults to `undefined`] |
| **workflowInput** | [WorkflowInput](WorkflowInput.md) |  | |

### Return type

[**ProjectDetailSchema**](ProjectDetailSchema.md)

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

