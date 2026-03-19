from __future__ import annotations

from dataclasses import asdict, dataclass


DEFAULT_RETRY_LIMIT = 3
DEFAULT_MANUAL_MODE_AFTER = 3


@dataclass(frozen=True)
class ActionContract:
    name: str
    description: str
    required_params: list[str]
    optional_params: list[str]
    outputs: list[str]
    retry_limit: int = DEFAULT_RETRY_LIMIT
    manual_mode_after: int = DEFAULT_MANUAL_MODE_AFTER


COMMON_REQUIRED_PARAMS = ["job_id", "build_id", "spec_path", "builder"]
COMMON_OPTIONAL_PARAMS = ["node_selector", "timeout_sec", "retry_limit", "manual_mode_after"]
COMMON_OUTPUTS = [
    "action",
    "status",
    "job_id",
    "build_id",
    "attempt",
    "manual_mode",
    "message",
    "artifacts",
    "next_actions",
    "error_code",
]


ACTION_CONTRACTS = [
    ActionContract(
        name="check_host_env",
        description="Validate host prerequisites and builder dependencies.",
        required_params=COMMON_REQUIRED_PARAMS,
        optional_params=COMMON_OPTIONAL_PARAMS + ["require_vmware", "require_disk_gb", "require_memory_mb"],
        outputs=COMMON_OUTPUTS,
    ),
    ActionContract(
        name="bootstrap_vm",
        description="Create target VMs, apply base resources, and wait until SSH is reachable.",
        required_params=COMMON_REQUIRED_PARAMS + ["base_image"],
        optional_params=COMMON_OPTIONAL_PARAMS
        + ["vm_hardware_version", "cpu", "memory_mb", "disk_gb", "network_name"],
        outputs=COMMON_OUTPUTS,
    ),
    ActionContract(
        name="push_packages",
        description="Distribute offline packages to target nodes.",
        required_params=COMMON_REQUIRED_PARAMS + ["package_set", "destination_dir"],
        optional_params=COMMON_OPTIONAL_PARAMS + ["checksum_verify"],
        outputs=COMMON_OUTPUTS,
    ),
    ActionContract(
        name="render_and_apply_configs",
        description="Render templates and apply service configs on target nodes.",
        required_params=COMMON_REQUIRED_PARAMS + ["template_group", "variables_file", "service_name"],
        optional_params=COMMON_OPTIONAL_PARAMS,
        outputs=COMMON_OUTPUTS,
    ),
    ActionContract(
        name="validate_cluster",
        description="Run connectivity, health, and sample workload checks.",
        required_params=COMMON_REQUIRED_PARAMS + ["checks"],
        optional_params=COMMON_OPTIONAL_PARAMS + ["stop_on_first_failure"],
        outputs=COMMON_OUTPUTS,
    ),
    ActionContract(
        name="export_artifact",
        description="Export VM artifacts and generate delivery metadata.",
        required_params=COMMON_REQUIRED_PARAMS + ["export_format", "output_dir"],
        optional_params=COMMON_OPTIONAL_PARAMS + ["include_docs"],
        outputs=COMMON_OUTPUTS,
    ),
]


def describe_actions() -> dict[str, object]:
    return {
        "rules": {
            "read_source_code": False,
            "use_scripts_as_api_only": True,
            "default_retry_limit": DEFAULT_RETRY_LIMIT,
            "manual_mode_after": DEFAULT_MANUAL_MODE_AFTER,
        },
        "actions": [asdict(action) for action in ACTION_CONTRACTS],
    }
