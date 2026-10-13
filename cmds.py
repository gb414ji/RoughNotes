SELECT IS_SRVROLEMEMBER('sysadmin');
SELECT * FROM fn_my_permissions(NULL, 'SERVER');
SELECT dp.permission_name, dp.state_desc, pr.name
FROM sys.server_permissions dp
JOIN sys.server_principals pr ON dp.grantee_principal_id = pr.principal_id;



SELECT @@VERSION;
SELECT SERVERPROPERTY('ProductVersion'), SERVERPROPERTY('ProductLevel');
SELECT name, is_disabled FROM sys.server_principals WHERE type = 'S';
SELECT * FROM sys.dm_server_services;



-- What can your specific low-priv login actually see with this permission set?
SELECT name, database_id, create_date FROM sys.databases;

-- Confirm which role your current login is actually mapped to
SELECT rp.name AS role_name, mp.name AS member_name
FROM sys.server_role_members rm
JOIN sys.server_principals rp ON rm.role_principal_id = rp.principal_id
JOIN sys.server_principals mp ON rm.member_principal_id = mp.principal_id;

-- Does your login have permission to list or access other databases' data (not just metadata)?
SELECT HAS_DBACCESS('master'), HAS_DBACCESS('msdb'), HAS_DBACCESS('model');







-- Which databases exist, and are any of them higher-value targets?
SELECT name, state_desc, is_trustworthy_on FROM sys.databases;

-- Is xp_cmdshell enabled? (This is the #1 precondition for RCE via SQLi in MSSQL)
SELECT name, value, value_in_use FROM sys.configurations WHERE name = 'xp_cmdshell';

-- Are there other dangerous extended procedures enabled?
SELECT name, value_in_use FROM sys.configurations 
WHERE name IN ('Ole Automation Procedures', 'Ad Hoc Distributed Queries', 'clr enabled');




SELECT pr.name AS can_impersonate, pe.permission_name
FROM sys.server_permissions pe
JOIN sys.server_principals pr ON pe.grantor_principal_id = pr.principal_id
WHERE pe.permission_name = 'IMPERSONATE';



SELECT * FROM sys.dm_server_audit_status;
SELECT * FROM sys.server_audits;


SELECT name, value_in_use FROM sys.configurations 
WHERE name IN ('Ole Automation Procedures', 'Ad Hoc Distributed Queries');
