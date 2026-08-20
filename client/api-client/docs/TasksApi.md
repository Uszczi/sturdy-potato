# TasksApi

All URIs are relative to *http://localhost*

| Method                                                         | HTTP request                 | Description   |
| -------------------------------------------------------------- | ---------------------------- | ------------- |
| [**apiTasksCountRetrieve**](TasksApi.md#apitaskscountretrieve) | **GET** /api/tasks/count/    | Count Tasks   |
| [**apiTasksCreate**](TasksApi.md#apitaskscreate)               | **POST** /api/tasks/         | Create Task   |
| [**apiTasksDestroy**](TasksApi.md#apitasksdestroy)             | **DELETE** /api/tasks/{id}/  | Delete Task   |
| [**apiTasksList**](TasksApi.md#apitaskslist)                   | **GET** /api/tasks/          | List Tasks    |
| [**apiTasksOpenList**](TasksApi.md#apitasksopenlist)           | **GET** /api/tasks/open/     | Open Tasks    |
| [**apiTasksPartialUpdate**](TasksApi.md#apitaskspartialupdate) | **PATCH** /api/tasks/{id}/   | Update Task   |
| [**apiTasksReorderCreate**](TasksApi.md#apitasksreordercreate) | **POST** /api/tasks/reorder/ | Reorder Tasks |
| [**apiTasksRetrieve**](TasksApi.md#apitasksretrieve)           | **GET** /api/tasks/{id}/     | Retrieve Task |
| [**apiTasksViewList**](TasksApi.md#apitasksviewlist)           | **GET** /api/tasks/view/     | View Tasks    |

## apiTasksCountRetrieve

> TaskCountSchema apiTasksCountRetrieve(status)

Count Tasks

### Example

```ts
import {
  Configuration,
  TasksApi,
} from '';
import type { ApiTasksCountRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TasksApi(config);

  const body = {
    // TaskStatus (optional)
    status: ...,
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

| Name       | Type         | Description | Notes                                                   |
| ---------- | ------------ | ----------- | ------------------------------------------------------- |
| **status** | `TaskStatus` |             | [Optional] [Defaults to `undefined`] [Enum: open, done] |

### Return type

[**TaskCountSchema**](TaskCountSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`

### HTTP response details

| Status code | Description         | Response headers |
| ----------- | ------------------- | ---------------- |
| **200**     | Successful Response | -                |
| **422**     | Validation Error    | -                |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

## apiTasksCreate

> TaskSchema apiTasksCreate(taskCreateInput)

Create Task

### Example

```ts
import {
  Configuration,
  TasksApi,
} from '';
import type { ApiTasksCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TasksApi(config);

  const body = {
    // TaskCreateInput
    taskCreateInput: ...,
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

| Name                | Type                                  | Description | Notes |
| ------------------- | ------------------------------------- | ----------- | ----- |
| **taskCreateInput** | [TaskCreateInput](TaskCreateInput.md) |             |       |

### Return type

[**TaskSchema**](TaskSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

### HTTP response details

| Status code | Description         | Response headers |
| ----------- | ------------------- | ---------------- |
| **201**     | Successful Response | -                |
| **422**     | Validation Error    | -                |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

## apiTasksDestroy

> apiTasksDestroy(id)

Delete Task

### Example

```ts
import { Configuration, TasksApi } from "";
import type { ApiTasksDestroyRequest } from "";

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TasksApi(config);

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

| Name   | Type     | Description | Notes                     |
| ------ | -------- | ----------- | ------------------------- |
| **id** | `number` |             | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`

### HTTP response details

| Status code | Description         | Response headers |
| ----------- | ------------------- | ---------------- |
| **204**     | Successful Response | -                |
| **422**     | Validation Error    | -                |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

## apiTasksList

> Array&lt;TaskSchema&gt; apiTasksList()

List Tasks

### Example

```ts
import { Configuration, TasksApi } from "";
import type { ApiTasksListRequest } from "";

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TasksApi(config);

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

[**Array&lt;TaskSchema&gt;**](TaskSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`

### HTTP response details

| Status code | Description         | Response headers |
| ----------- | ------------------- | ---------------- |
| **200**     | Successful Response | -                |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

## apiTasksOpenList

> Array&lt;TaskSchema&gt; apiTasksOpenList(limit)

Open Tasks

### Example

```ts
import { Configuration, TasksApi } from "";
import type { ApiTasksOpenListRequest } from "";

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TasksApi(config);

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

| Name      | Type     | Description | Notes                                |
| --------- | -------- | ----------- | ------------------------------------ |
| **limit** | `number` |             | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;TaskSchema&gt;**](TaskSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`

### HTTP response details

| Status code | Description         | Response headers |
| ----------- | ------------------- | ---------------- |
| **200**     | Successful Response | -                |
| **422**     | Validation Error    | -                |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

## apiTasksPartialUpdate

> TaskSchema apiTasksPartialUpdate(id, taskUpdateInput)

Update Task

### Example

```ts
import {
  Configuration,
  TasksApi,
} from '';
import type { ApiTasksPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TasksApi(config);

  const body = {
    // number
    id: 56,
    // TaskUpdateInput
    taskUpdateInput: ...,
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

| Name                | Type                                  | Description | Notes                     |
| ------------------- | ------------------------------------- | ----------- | ------------------------- |
| **id**              | `number`                              |             | [Defaults to `undefined`] |
| **taskUpdateInput** | [TaskUpdateInput](TaskUpdateInput.md) |             |                           |

### Return type

[**TaskSchema**](TaskSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

### HTTP response details

| Status code | Description         | Response headers |
| ----------- | ------------------- | ---------------- |
| **200**     | Successful Response | -                |
| **422**     | Validation Error    | -                |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

## apiTasksReorderCreate

> apiTasksReorderCreate(reorderInput)

Reorder Tasks

### Example

```ts
import {
  Configuration,
  TasksApi,
} from '';
import type { ApiTasksReorderCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TasksApi(config);

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

| Name             | Type                            | Description | Notes |
| ---------------- | ------------------------------- | ----------- | ----- |
| **reorderInput** | [ReorderInput](ReorderInput.md) |             |       |

### Return type

`void` (Empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

### HTTP response details

| Status code | Description         | Response headers |
| ----------- | ------------------- | ---------------- |
| **204**     | Successful Response | -                |
| **422**     | Validation Error    | -                |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

## apiTasksRetrieve

> TaskSchema apiTasksRetrieve(id)

Retrieve Task

### Example

```ts
import { Configuration, TasksApi } from "";
import type { ApiTasksRetrieveRequest } from "";

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TasksApi(config);

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

| Name   | Type     | Description | Notes                     |
| ------ | -------- | ----------- | ------------------------- |
| **id** | `number` |             | [Defaults to `undefined`] |

### Return type

[**TaskSchema**](TaskSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`

### HTTP response details

| Status code | Description         | Response headers |
| ----------- | ------------------- | ---------------- |
| **200**     | Successful Response | -                |
| **422**     | Validation Error    | -                |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

## apiTasksViewList

> Array&lt;TaskSchema&gt; apiTasksViewList(view, project, tz)

View Tasks

### Example

```ts
import { Configuration, TasksApi } from "";
import type { ApiTasksViewListRequest } from "";

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TasksApi(config);

  const body = {
    // 'inbox' | 'today' | 'upcoming' | 'all' (optional)
    view: view_example,
    // number (optional)
    project: 56,
    // string (optional)
    tz: tz_example,
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

| Name        | Type                                | Description | Notes                                                                          |
| ----------- | ----------------------------------- | ----------- | ------------------------------------------------------------------------------ |
| **view**    | `inbox`, `today`, `upcoming`, `all` |             | [Optional] [Defaults to `&#39;inbox&#39;`] [Enum: inbox, today, upcoming, all] |
| **project** | `number`                            |             | [Optional] [Defaults to `undefined`]                                           |
| **tz**      | `string`                            |             | [Optional] [Defaults to `&#39;UTC&#39;`]                                       |

### Return type

[**Array&lt;TaskSchema&gt;**](TaskSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`

### HTTP response details

| Status code | Description         | Response headers |
| ----------- | ------------------- | ---------------- |
| **200**     | Successful Response | -                |
| **422**     | Validation Error    | -                |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
