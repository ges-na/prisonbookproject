# Changelog

## 2026-05-26
- User/auth updates:
	- Switched from default User model to custom User model
	- Switched to email login, suppressed username field
	- Added django_registration for user registration, reset password flows
	- Created `User.is_contributor` status
- Contributor site:
	- Created forms for authenticated contributors to add people and letters
	- Created contributor profile page
- Email service integration (SparkPost)
- Added ProblemNote model, currently only in use by contributor forms

## 2025-11-21
- Added daily database backup to AWS (GitHub Action to pg_dump .sql format to S3 bucket)
- Tested restore from backup locally and on Fly
- Non-superusers can now edit prison address, notes, and restrictions

## 2025-08-19
- Add filters to People table
- Add custom Person queryset/manager
- Add No Longer In Custody labels / filter
- Remove Just PADA workflow status
- Bulk Letter discard action

## 2025-08-17
- Restructured project (added src/ dir)
- Added fly.io dev server config
- Environment-based color scheme support
- Project Python3.10 -> 3.12
