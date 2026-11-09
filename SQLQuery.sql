create database URBASE
go
use URBASE
go 

create table Homeworks
(
	Id int primary key identity(1,1),
	Subject Nvarchar(50) not null,
	RecordingDate date not null,
	DateOfExpire date not null,
	Homework nvarchar(1000) not null,
	Username nvarchar(100),
	UserTgId nvarchar(500) not null
);