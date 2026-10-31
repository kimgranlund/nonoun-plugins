# Software catalog: component, release and installation

This is an authored illustration with synthetic package metadata and policies.
It makes no claim about an installed product, security boundary or executed test.

## Request and source material

“Catalog the renderer in our application, identify what is deployed, and state
whether the catalog supports giving it access to the application's cache.”

| Source record | Native assertion |
| --- | --- |
| `lock:atlas-7` | Application Atlas pins package `MosaicRender` at release `3.2`; that release depends on package `ShadeMath` at `1.4`. |
| `inventory:stage-12` | Installation `stage:renderer-12` deploys the `MosaicRender` `3.2` artifact in staging. |
| `assembly:atlas-7` | Installation `stage:renderer-12` is a runtime component of deployment `stage:atlas-7`. |
| `policy:stage-5` | Principal `stage:renderer-service` may read resource `stage:render-cache`; it may not write it. The policy does not bind that principal to an installation. |

## A sufficient model

| Identity | Kind and definition |
| --- | --- |
| `kind:renderer` | Software role: produces a rendered output from an input representation |
| `pkg:mosaic-render` | Package family, human label `MosaicRender` |
| `release:mosaic-render/3.2` | Release artifact belonging to that package family |
| `release:shade-math/1.4` | Dependency release identified by the lock record |
| `stage:renderer-12` | Installation of the renderer release, in a particular environment |
| `stage:renderer-service` | Authorization principal; distinct from package, release and installation |

Define `release_of` from release to package, `installed_from` from installation to
release, and `depends_on` between pinned releases. The assembly's `component_of`
relates two deployed instances. Role classification uses `serves_role`; it is
independent of containment, version selection and authorization.

The lock and inventory records own deployment facts. A generated dependency graph
and catalog table may project them. A semantic registry owns relation definitions;
the authorization policy remains the authority for its permission decisions.

## Decisions and neighboring failures

| Decision | Outcome and evidence |
| --- | --- |
| Show MosaicRender 3.2 as installed in staging | Supported by the exact release and installation inventory |
| Show ShadeMath 1.4 as a declared dependency | Supported by the lock record; this alone does not establish a separate deployed installation |
| Infer ShadeMath is a subtype of MosaicRender | Invalid: dependency is not classification |
| Report that the service principal may read the cache | Supported within `policy:stage-5` and its staging scope |
| Grant cache writes because the renderer is part of Atlas | Unsupported: composition confers no permission and the policy explicitly denies writes |
| Claim the installed renderer actually has the principal's read access | Unknown until principal-to-installation binding and enforcement evidence are supplied |

When production later installs release 3.3, add its installation and release edges.
Retain the staging inventory's 3.2 identity and applicable policy version. A query
for the staging snapshot must not resolve through a mutable “current release.”

Schema validation can require an installation to name a release. Cross-record
checks can verify the reference exists. Neither check proves the runtime enforces
the policy; a separate enforcement integration must mediate actual access.

Use [relationships](../references/relationships.md), [validation](../references/validation.md),
and [evolution](../references/evolution.md) for the reusable method.
