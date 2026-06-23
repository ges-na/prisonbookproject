# Changelog

## 2026-06-23
- Switched ProblemNote -> PersonIssue / LetterIssue
    - Added issue choices for returned packages and wrong prison to appropriate issue types
    - Resolve issue admin action
    - Add issue from person/letter forms
    - Add issue field to list views
    - Contrib profile links to appropriate note types
- Sanitize email to lowercase for registration, login, password change
- Added first & last names to registration form
- Rearranged admin
- Added permissions to change active, contributor, and staff statuses
    - Added admin actions to change user permissions
- Started adding tests
- Standardized permissions with decorator

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
