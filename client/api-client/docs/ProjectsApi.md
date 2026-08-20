# ProjectsApi

All URIs are relative to *http://localhost*

| Method                                                                  | HTTP request                    | Description      |
| ----------------------------------------------------------------------- | ------------------------------- | ---------------- |
| [**apiProjectsCreate**](ProjectsApi.md#apiprojectscreate)               | **POST** /api/projects/         | Create Project   |
| [**apiProjectsDestroy**](ProjectsApi.md#apiprojectsdestroy)             | **DELETE** /api/projects/{id}/  | Delete Project   |
| [**apiProjectsList**](ProjectsApi.md#apiprojectslist)                   | **GET** /api/projects/          | List Projects    |
| [**apiProjectsPartialUpdate**](ProjectsApi.md#apiprojectspartialupdate) | **PATCH** /api/projects/{id}/   | Update Project   |
| [**apiProjectsReorderCreate**](ProjectsApi.md#apiprojectsreordercreate) | **POST** /api/projects/reorder/ | Reorder Projects |
| [**apiProjectsRetrieve**](ProjectsApi.md#apiprojectsretrieve)           | **GET** /api/projects/{id}/     | Retrieve Project |

## apiProjectsCreate

> ProjectSchema apiProjectsCreate(projectCreateInput)

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

| Name                   | Type                                        | Description | Notes |
| ---------------------- | ------------------------------------------- | ----------- | ----- |
| **projectCreateInput** | [ProjectCreateInput](ProjectCreateInput.md) |             |       |

### Return type

[**ProjectSchema**](ProjectSchema.md)

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

## apiProjectsDestroy

> apiProjectsDestroy(id)

Delete Project

### Example

```ts
import { Configuration, ProjectsApi } from "";
import type { ApiProjectsDestroyRequest } from "";

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

## apiProjectsList

> Array&lt;ProjectSchema&gt; apiProjectsList()

List Projects

### Example

```ts
import { Configuration, ProjectsApi } from "";
import type { ApiProjectsListRequest } from "";

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ProjectsApi(config);

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

| Status code | Description         | Response headers |
| ----------- | ------------------- | ---------------- |
| **200**     | Successful Response | -                |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

## apiProjectsPartialUpdate

> ProjectSchema apiProjectsPartialUpdate(id, projectUpdateInput)

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

| Name                   | Type                                        | Description | Notes                     |
| ---------------------- | ------------------------------------------- | ----------- | ------------------------- |
| **id**                 | `number`                                    |             | [Defaults to `undefined`] |
| **projectUpdateInput** | [ProjectUpdateInput](ProjectUpdateInput.md) |             |                           |

### Return type

[**ProjectSchema**](ProjectSchema.md)

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

## apiProjectsReorderCreate

> apiProjectsReorderCreate(reorderInput)

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

## apiProjectsRetrieve

> ProjectSchema apiProjectsRetrieve(id)

Retrieve Project

### Example

```ts
import { Configuration, ProjectsApi } from "";
import type { ApiProjectsRetrieveRequest } from "";

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

| Name   | Type     | Description | Notes                     |
| ------ | -------- | ----------- | ------------------------- |
| **id** | `number` |             | [Defaults to `undefined`] |

### Return type

[**ProjectSchema**](ProjectSchema.md)

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
