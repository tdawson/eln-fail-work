# eln-fail-work
Track eln rpm build failures, with notes on their failures

== Where do we get the data

=== distrobuildsync status
* http://distrobuildsync-eln-ops.apps.stream.rdu2.redhat.com/status
* http://distrobuildsync-eln-ops.apps.stream.rdu2.redhat.com/status.json

=== koji
* koji -q list-tagged --latest eln

