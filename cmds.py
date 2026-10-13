SELECT IS_SRVROLEMEMBER('sysadmin');
SELECT * FROM fn_my_permissions(NULL, 'SERVER');
SELECT dp.permission_name, dp.state_desc, pr.name
FROM sys.server_permissions dp
JOIN sys.server_principals pr ON dp.grantee_principal_id = pr.principal_id;



SELECT @@VERSION;
SELECT SERVERPROPERTY('ProductVersion'), SERVERPROPERTY('ProductLevel');
SELECT name, is_disabled FROM sys.server_principals WHERE type = 'S';
SELECT * FROM sys.dm_server_services;
