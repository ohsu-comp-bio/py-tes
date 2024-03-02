<!-- markdownlint-disable -->

# API Overview

## Modules

- [`client`](./client.md#module-client): TES access methods and helper functions.
- [`models`](./models.md#module-models): TES models, converters, validators and helpers.
- [`utils`](./utils.md#module-utils): Exceptions and utilities.

## Classes

- [`client.HTTPClient`](./client.md#class-httpclient): HTTP client class for interacting with the TES API.
- [`models.Base`](./models.md#class-base): `attrs` base class for all TES and helper models.
- [`models.CancelTaskRequest`](./models.md#class-canceltaskrequest): `attrs` model class for `POST /tasks/{id}:cancel` request parameters.
- [`models.CancelTaskResponse`](./models.md#class-canceltaskresponse): TES `tesCancelTaskResponse` `attrs` model class.
- [`models.CreateTaskResponse`](./models.md#class-createtaskresponse): TES `tesCreateTaskResponse` `attrs` model class.
- [`models.Executor`](./models.md#class-executor): TES `tesExecutor` `attrs` model class.
- [`models.ExecutorLog`](./models.md#class-executorlog): TES `tesExecutorLog` `attrs` model class.
- [`models.GetTaskRequest`](./models.md#class-gettaskrequest): `attrs` model class for `GET /tasks/{id}` request parameters.
- [`models.Input`](./models.md#class-input): TES `tesInput` `attrs` model class.
- [`models.ListTasksRequest`](./models.md#class-listtasksrequest): `attrs` model class for `GET /tasks` request parameters.
- [`models.ListTasksResponse`](./models.md#class-listtasksresponse): TES `tesListTasksResponse` `attrs` model class.
- [`models.Output`](./models.md#class-output): TES `tesOutput` `attrs` model class.
- [`models.OutputFileLog`](./models.md#class-outputfilelog): TES `tesOutputFileLog` `attrs` model class.
- [`models.Resources`](./models.md#class-resources): TES `tesResources` `attrs` model class.
- [`models.ServiceInfo`](./models.md#class-serviceinfo): TES `tesServiceInfo` `attrs` model class.
- [`models.ServiceInfoRequest`](./models.md#class-serviceinforequest): `attrs` model class for `GET /service-info` request parameters.
- [`models.Task`](./models.md#class-task): TES `tesTask` `attrs` model class.
- [`models.TaskLog`](./models.md#class-tasklog): TES `tesTaskLog` `attrs` model class.
- [`utils.TimeoutError`](./utils.md#class-timeouterror)
- [`utils.UnmarshalError`](./utils.md#class-unmarshalerror): Raised when a JSON string cannot be unmarshalled to a TES model.

## Functions

- [`client.process_url`](./client.md#function-process_url)
- [`models.datetime_json_handler`](./models.md#function-datetime_json_handler): JSON handler for `datetime` objects.
- [`models.int64conv`](./models.md#function-int64conv): Convert string to `int64`.
- [`models.list_of`](./models.md#function-list_of): `attrs` validator for lists of a given type.
- [`models.strconv`](./models.md#function-strconv): Explicitly cast a string-like value or list thereof to string(s).
- [`models.timestampconv`](./models.md#function-timestampconv): Convert string to `datetime`.
- [`utils.camel_to_snake`](./utils.md#function-camel_to_snake): Converts camelCase to snake_case.
- [`utils.unmarshal`](./utils.md#function-unmarshal): Unmarshal a JSON string to a TES model.


---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
