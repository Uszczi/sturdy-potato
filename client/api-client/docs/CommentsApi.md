# CommentsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**apiTaskCommentsCreate**](CommentsApi.md#apitaskcommentscreate) | **POST** /api/workspaces/{workspace_id}/tasks/{task_id}/comments/ | Create Comment |
| [**apiTaskCommentsDestroy**](CommentsApi.md#apitaskcommentsdestroy) | **DELETE** /api/workspaces/{workspace_id}/tasks/{task_id}/comments/{comment_id}/ | Delete Comment |
| [**apiTaskCommentsList**](CommentsApi.md#apitaskcommentslist) | **GET** /api/workspaces/{workspace_id}/tasks/{task_id}/comments/ | List Comments |
| [**apiTaskCommentsPartialUpdate**](CommentsApi.md#apitaskcommentspartialupdate) | **PATCH** /api/workspaces/{workspace_id}/tasks/{task_id}/comments/{comment_id}/ | Update Comment |



## apiTaskCommentsCreate

> CommentSchema apiTaskCommentsCreate(taskId, workspaceId, commentCreateInput)

Create Comment

### Example

```ts
import {
  Configuration,
  CommentsApi,
} from '';
import type { ApiTaskCommentsCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CommentsApi(config);

  const body = {
    // number
    taskId: 56,
    // number
    workspaceId: 56,
    // CommentCreateInput
    commentCreateInput: ...,
  } satisfies ApiTaskCommentsCreateRequest;

  try {
    const data = await api.apiTaskCommentsCreate(body);
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
| **taskId** | `number` |  | [Defaults to `undefined`] |
| **workspaceId** | `number` |  | [Defaults to `undefined`] |
| **commentCreateInput** | [CommentCreateInput](CommentCreateInput.md) |  | |

### Return type

[**CommentSchema**](CommentSchema.md)

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


## apiTaskCommentsDestroy

> apiTaskCommentsDestroy(taskId, commentId, workspaceId)

Delete Comment

### Example

```ts
import {
  Configuration,
  CommentsApi,
} from '';
import type { ApiTaskCommentsDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CommentsApi(config);

  const body = {
    // number
    taskId: 56,
    // number
    commentId: 56,
    // number
    workspaceId: 56,
  } satisfies ApiTaskCommentsDestroyRequest;

  try {
    const data = await api.apiTaskCommentsDestroy(body);
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
| **taskId** | `number` |  | [Defaults to `undefined`] |
| **commentId** | `number` |  | [Defaults to `undefined`] |
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


## apiTaskCommentsList

> Array&lt;CommentSchema&gt; apiTaskCommentsList(taskId, workspaceId)

List Comments

### Example

```ts
import {
  Configuration,
  CommentsApi,
} from '';
import type { ApiTaskCommentsListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CommentsApi(config);

  const body = {
    // number
    taskId: 56,
    // number
    workspaceId: 56,
  } satisfies ApiTaskCommentsListRequest;

  try {
    const data = await api.apiTaskCommentsList(body);
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
| **taskId** | `number` |  | [Defaults to `undefined`] |
| **workspaceId** | `number` |  | [Defaults to `undefined`] |

### Return type

[**Array&lt;CommentSchema&gt;**](CommentSchema.md)

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


## apiTaskCommentsPartialUpdate

> CommentSchema apiTaskCommentsPartialUpdate(taskId, commentId, workspaceId, commentUpdateInput)

Update Comment

### Example

```ts
import {
  Configuration,
  CommentsApi,
} from '';
import type { ApiTaskCommentsPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CommentsApi(config);

  const body = {
    // number
    taskId: 56,
    // number
    commentId: 56,
    // number
    workspaceId: 56,
    // CommentUpdateInput
    commentUpdateInput: ...,
  } satisfies ApiTaskCommentsPartialUpdateRequest;

  try {
    const data = await api.apiTaskCommentsPartialUpdate(body);
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
| **taskId** | `number` |  | [Defaults to `undefined`] |
| **commentId** | `number` |  | [Defaults to `undefined`] |
| **workspaceId** | `number` |  | [Defaults to `undefined`] |
| **commentUpdateInput** | [CommentUpdateInput](CommentUpdateInput.md) |  | |

### Return type

[**CommentSchema**](CommentSchema.md)

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

