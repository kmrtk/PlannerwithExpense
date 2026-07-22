output "public_ip" {
  description = "EC2のパブリックIP（Elastic IP）"
  value       = aws_eip.app.public_ip
}

output "ssh_command" {
  description = "SSH接続コマンド"
  value       = "ssh -i <秘密鍵のパス> ec2-user@${aws_eip.app.public_ip}"
}

output "rds_endpoint" {
  description = "RDSのエンドポイント（ホスト名:ポート）"
  value       = aws_db_instance.app.endpoint
}
