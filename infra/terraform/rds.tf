data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_db_subnet_group" "app" {
  name       = "plannerwithexpense-db-subnet-group"
  subnet_ids = data.aws_subnets.default.ids

  tags = {
    Name = "plannerwithexpense-db-subnet-group"
  }
}

resource "aws_security_group" "rds" {
  name        = "plannerwithexpense-rds-sg"
  description = "PlannerwithExpense RDS - MySQL from EC2 only"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "MySQL from EC2 only"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  tags = {
    Name = "plannerwithexpense-rds-sg"
  }
}

resource "aws_db_instance" "app" {
  identifier     = "plannerwithexpense-db"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"

  allocated_storage = 20
  storage_type      = "gp2"

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.app.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false

  skip_final_snapshot     = true
  backup_retention_period = 1

  tags = {
    Name = "plannerwithexpense-db"
  }
}
