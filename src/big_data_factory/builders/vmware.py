from __future__ import annotations


class VMwareBuilder:
    """Placeholder for the VMware execution adapter."""

    name = "vmware"

    def validate_host(self) -> None:
        raise NotImplementedError("VMware host validation is not implemented yet.")

    def build(self) -> None:
        raise NotImplementedError("VMware build workflow is not implemented yet.")
