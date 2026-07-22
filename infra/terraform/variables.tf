variable "aws_region" {
  description = "リソースを作成するAWSリージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "instance_type" {
  description = "EC2インスタンスタイプ（無料枠対象）"
  type        = string
  default     = "t3.micro"
}

variable "ssh_public_key_path" {
  description = "EC2に登録するSSH公開鍵のローカルパス"
  type        = string
}

variable "my_ip_cidr" {
  description = "SSH(22番)・HTTP(80番)アクセスを許可する自分のグローバルIP（例: 203.0.113.1/32）"
  type        = string
}
