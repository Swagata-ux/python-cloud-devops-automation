# Python Cloud DevOps Automation 🚀

A collection of production-ready Python scripts for cloud infrastructure automation, monitoring, and DevOps tasks. This repository contains practical tools for AWS, log analysis, service monitoring, and cost optimization.

## 📋 Table of Contents

- [Overview](#overview)
- [Scripts](#scripts)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This repository is a year-long project focused on building practical Python automation tools for cloud and DevOps engineers. Each script solves real-world problems encountered in production environments.

### Key Features
- ✅ Production-ready code with error handling
- ✅ Comprehensive logging and monitoring
- ✅ AWS integration with boto3
- ✅ Cost optimization tools
- ✅ Service health monitoring
- ✅ Log analysis and reporting

## 📁 Scripts

### 1. Web Server Log Analyzer
**File:** `14_01_2026_log_analyzer.py`

Analyzes web server logs to identify top IP addresses and error rates.

```bash
python 14_01_2026_log_analyzer.py
```

**Features:**
- Parses Apache/Nginx log formats
- Identifies top 3 most frequent IP addresses
- Calculates error rate (4xx/5xx status codes)
- Handles malformed log entries gracefully

### 2. Cloud Volume Detector
**File:** `15_01_2026_volume_detector.py`

Detects orphaned and zombie cloud storage volumes to optimize costs.

```bash
python 15_01_2026_volume_detector.py
```

**Features:**
- Identifies orphaned volumes (unattached)
- Detects zombie volumes (attached to non-existent instances)
- Calculates potential cost savings
- Supports dry-run mode
- O(N+M) time complexity for large datasets

### 3. Service Health Checker
**File:** `16_01_2026_health_checker_simple.py`

Monitors microservice health with exponential backoff retry logic.

```bash
python 16_01_2026_health_checker_simple.py
```

**Features:**
- Exponential backoff retry mechanism (1s, 2s, 4s)
- Response time tracking
- Comprehensive health reporting
- Configurable retry limits
- Professional logging

### 4. EC2 Idle Instance Detector
**File:** `17_01_2026_ec2_idle_detector_aws.py`

Detects and safely terminates idle EC2 instances based on CPU utilization.

```bash
# Dry run (safe preview)
python 17_01_2026_ec2_idle_detector_aws.py --region us-east-1

# Execute termination (DANGEROUS!)
python 17_01_2026_ec2_idle_detector_aws.py --execute --cpu-threshold 5.0 --idle-hours 24
```

**Features:**
- Real AWS integration with boto3
- CloudWatch CPU metrics analysis
- Safety checks and protection tags
- Dry-run mode for safe testing
- Configurable thresholds and regions

**Required IAM Permissions:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:TerminateInstances",
                "cloudwatch:GetMetricStatistics"
            ],
            "Resource": "*"
        }
    ]
}
```

### 5. API Performance Analyzer
**File:** `18_01_2026_api_analyzer.py`

Analyzes API request logs to identify the slowest endpoints.

```bash
python 18_01_2026_api_analyzer.py
```

**Features:**
- Multiple log format support (Apache, custom, JSON)
- Top 10 slowest endpoints analysis
- Average response time calculations
- Error handling for malformed logs

## 🛠 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Dependencies
```bash
# Core dependencies
pip install boto3 botocore

# For AWS integration
pip install boto3

# Configure AWS credentials
aws configure
```

### Clone Repository
```bash
git clone https://github.com/Swagata-ux/python-cloud-devops-automation.git
cd python-cloud-devops-automation
```

## 🚀 Usage

### Quick Start
```bash
# Test log analyzer
python 14_01_2026_log_analyzer.py

# Test volume detector
python 15_01_2026_volume_detector.py

# Test health checker
python 16_01_2026_health_checker_simple.py

# Test API analyzer
python 18_01_2026_api_analyzer.py
```

### AWS Configuration
For AWS-related scripts, ensure your credentials are configured:

```bash
# Option 1: AWS CLI
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Option 3: IAM roles (recommended for EC2/Lambda)
```

### Production Usage

#### EC2 Instance Management
```bash
# Check idle instances (safe)
python 17_01_2026_ec2_idle_detector_aws.py --region us-west-2

# Terminate idle instances (CAREFUL!)
python 17_01_2026_ec2_idle_detector_aws.py --execute --cpu-threshold 10 --idle-hours 48
```

#### Log Analysis
```bash
# Analyze custom log file
python 14_01_2026_log_analyzer.py /path/to/access.log

# API performance analysis
python 18_01_2026_api_analyzer.py /path/to/api.log
```

## 📊 Sample Outputs

### Volume Detector Report
```
Cloud Volume Analysis Report
========================================
Orphaned Volumes: 2
  • vol-002
  • vol-004

Zombie Volumes: 1
  • vol-003

Total Monthly Savings: $8.40
Annual Savings: $100.80
```

### Health Check Report
```
SERVICE HEALTH REPORT
======================================================================
Services UP: 3 | Services DOWN: 1
----------------------------------------------------------------------
✅ auth-service          UP   (2 attempts, 145.23ms)
✅ payment-gateway       UP   (1 attempts, 89.45ms)
✅ inventory-api         UP   (3 attempts, 234.67ms)
❌ user-service          DOWN (4 attempts)
```

## 🔧 Configuration

### Environment Variables
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default

# Script Configuration
CPU_THRESHOLD=5.0
IDLE_HOURS=24
MAX_RETRIES=3
```

### Protected Tags
Modify protected tags in EC2 detector:
```python
PROTECTED_TAGS = ['production', 'critical', 'database', 'staging']
```

## 🧪 Testing

Each script includes built-in test data and examples:

```bash
# Run with sample data
python script_name.py

# Most scripts support --help
python 17_01_2026_ec2_idle_detector_aws.py --help
```

## 📈 Roadmap

### Upcoming Features (2025)
- [ ] Kubernetes resource optimization
- [ ] Multi-cloud support (Azure, GCP)
- [ ] Cost optimization dashboards
- [ ] Automated alerting systems
- [ ] Infrastructure as Code generators
- [ ] Security compliance checkers
- [ ] Performance monitoring tools
- [ ] Backup automation scripts

### Monthly Themes
- **January**: AWS Cost Optimization
- **February**: Monitoring & Alerting
- **March**: Security & Compliance
- **April**: Kubernetes Automation
- **May**: Multi-Cloud Management
- **June**: CI/CD Pipeline Tools
- **July**: Infrastructure as Code
- **August**: Performance Optimization
- **September**: Disaster Recovery
- **October**: Observability Tools
- **November**: Security Automation
- **December**: Year-End Optimization

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 style guidelines
- Include comprehensive error handling
- Add logging for production use
- Include docstrings and type hints
- Test with sample data

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Swagata Banerjee**
- GitHub: [@Swagata-ux](https://github.com/Swagata-ux)
- LinkedIn: [Connect with me](https://linkedin.com/in/swagata-banerjee)

## 🙏 Acknowledgments

- AWS Documentation and Best Practices
- Python Community for excellent libraries
- DevOps Community for inspiration and feedback

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/Swagata-ux/python-cloud-devops-automation/issues) page
2. Create a new issue with detailed description
3. Include error logs and environment details

---

⭐ **Star this repository if you find it helpful!**

*This is a living project that will be continuously updated throughout 2025 with new automation tools and improvements.*