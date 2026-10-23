# T15 — System diagrams

The system diagrams are separate project files in `diagrams/`. Open their PNG or SVG files directly. The dashboard has only Overview, Sensor readings and My report; its navigation, markup, scripts and standalone preview do not include a System diagrams page.

The supplied `T15_use_case.png` and `T15_data_flow.png` are unchanged. The new `T15_data_flow_level1.svg` and PNG expand process 0 of the supplied context diagram. The SVG is an editable vector file; `scripts/create_level1.py` regenerates it using the Python standard library.

## Level 1 processes

| Process | Inputs | Outputs |
|---|---|---|
| 1.0 Authenticate device and store readings | Sensor data, device authentication, authentication record, previous hash | Validated reading and new hash in D1 |
| 2.0 Assess readings and serve risk warnings | D1 readings, tenant dashboard request | Readings, risk level and warnings for the tenant; risk summary for 4.0 |
| 3.0 Verify reading integrity | D1 readings and stored hashes; tenant verification request | Integrity result for the tenant and 4.0 |
| 4.0 Prepare report and landlord letter | Readings, risk summary, verification result, tenant request, language, optional photo and landlord details; Bedrock analysis | Tenant explanation, report and draft letter; stored report/photo record; tenant-approved report and letter for the landlord |

D1 holds readings and hashes; D2 holds reports and photo records; D3 represents proposed device authentication records. Repeated Tenant boxes identify the same external entity and reduce crossing arrows.

## Balance and scope

The external entities are the same four as the supplied context diagram: Device, Tenant, Landlord and Bedrock AI. The core flows are retained: device data in; tenant requests/photo/details in; tenant readings/risk/warnings/report out; processing data to Bedrock and analysis back; report/letter to the landlord. Language is an added field in the report request, as required by the updated dashboard specification.

This Level 1 view covers the core scope of that context diagram. The additional T17 weather/forecast integration is documented in `API_INTEGRATION.md`; the original context image has not been altered to introduce another external entity.

The diagram describes a proposed complete system. D3 authentication, photo processing, report persistence and delivery to a landlord are not claimed as implemented by the browser dashboard. The current interface keeps letter review under tenant control and never automatically sends a letter. No diagram or wireframe is used as a substitute for working dashboard code.
