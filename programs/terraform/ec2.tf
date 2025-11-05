resource "aws_instance" "example" {
  ami           = "ami-06fa3f12191aa3337"
  instance_type = var.size

  tags = {
    Name = "HelloWorld"
  }
}
