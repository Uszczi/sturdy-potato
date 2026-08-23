# WorkspacesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**apiWorkspacesCreate**](WorkspacesApi.md#apiworkspacescreate) | **POST** /api/workspaces/ | Create Workspace |
| [**apiWorkspacesList**](WorkspacesApi.md#apiworkspaceslist) | **GET** /api/workspaces/ | List Workspaces |
| [**apiWorkspacesRetrieve**](WorkspacesApi.md#apiworkspacesretrieve) | **GET** /api/workspaces/{workspace_id}/ | Retrieve Workspace |
| [**apiWorkspacesStatusesUpdate**](WorkspacesApi.md#apiworkspacesstatusesupdate) | **PUT** /api/workspaces/{workspace_id}/statuses/ | Set Workspace Workflow |



## apiWorkspacesCreate

> WorkspaceSchema apiWorkspacesCreate(workspaceCreateInput)

Create Workspace

### Example

```ts
import {
  Configuration,
  WorkspacesApi,
} from '';
import type { ApiWorkspacesCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WorkspacesApi(config);

  const body = {
    // WorkspaceCreateInput
    workspaceCreateInput: ...,
  } satisfies ApiWorkspacesCreateRequest;

  try {
    const data = await api.apiWorkspacesCreate(body);
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
| **workspaceCreateInput** | [WorkspaceCreateInput](WorkspaceCreateInput.md) |  | |

### Return type

[**WorkspaceSchema**](WorkspaceSchema.md)

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


## apiWorkspacesList

> Array&lt;WorkspaceSchema&gt; apiWorkspacesList()

List Workspaces

### Example

```ts
import {
  Configuration,
  WorkspacesApi,
} from '';
import type { ApiWorkspacesListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WorkspacesApi(config);

  try {
    const data = await api.apiWorkspacesList();
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

[**Array&lt;WorkspaceSchema&gt;**](WorkspaceSchema.md)

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


## apiWorkspacesRetrieve

> WorkspaceDetailSchema apiWorkspacesRetrieve(workspaceId)

Retrieve Workspace

One workspace, including the workflow the inbox board renders.

### Example

```ts
import {
  Configuration,
  WorkspacesApi,
} from '';
import type { ApiWorkspacesRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WorkspacesApi(config);

  const body = {
    // number
    workspaceId: 56,
  } satisfies ApiWorkspacesRetrieveRequest;

  try {
    const data = await api.apiWorkspacesRetrieve(body);
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

[**WorkspaceDetailSchema**](WorkspaceDetailSchema.md)

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


## apiWorkspacesStatusesUpdate

> WorkspaceDetailSchema apiWorkspacesStatusesUpdate(workspaceId, workflowInput)

Set Workspace Workflow

Replace the inbox board\&#39;s workflow, and the template new projects copy.  Projects that already exist keep their own snapshot and are untouched.

### Example

```ts
import {
  Configuration,
  WorkspacesApi,
} from '';
import type { ApiWorkspacesStatusesUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WorkspacesApi(config);

  const body = {
    // number
    workspaceId: 56,
    // WorkflowInput
    workflowInput: ...,
  } satisfies ApiWorkspacesStatusesUpdateRequest;

  try {
    const data = await api.apiWorkspacesStatusesUpdate(body);
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
| **workflowInput** | [WorkflowInput](WorkflowInput.md) |  | |

### Return type

[**WorkspaceDetailSchema**](WorkspaceDetailSchema.md)

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

