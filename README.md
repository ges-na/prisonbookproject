# Prison Book Project Database
 A workflow and data collection tool designed to track letters from incarcerated readers.

## Changelog
2025-11-21
* Added GitHub Action for daily database backup to AWS (pg_dump .sql format to S3 bucket)
* Tested backup and restore database  

2025-08-19
* Add filters to People table
* Add custom Person queryset/manager
* Add No Longer In Custody labels / filter
* Remove Just PADA workflow status
* Bulk Letter discard action

2025-08-17
* Restructured project (added `src/` dir)
* Added fly.io dev server config
* Environment-based color scheme support
* Project Python3.10 -> 3.12
