#!/bin/bash

# Configuration
PACKAGE_DIR="lambda_package"
ZIP_FILE="retail_ops_agent_lambda.zip"
PYTHON_VERSION="3.11"
PLATFORM="manylinux2014_x86_64"

echo "🚀 Starting Lambda packaging process..."

# 1. Clean up old artifacts
echo "🧹 Cleaning up old artifacts..."
rm -rf $PACKAGE_DIR $ZIP_FILE
mkdir $PACKAGE_DIR

# 2. Install dependencies for Linux x86_64
echo "📦 Installing dependencies for platform $PLATFORM..."
./.venv/bin/pip install \
  --platform $PLATFORM \
  --target $PACKAGE_DIR \
  --implementation cp \
  --python-version $PYTHON_VERSION \
  --only-binary=:all: \
  --upgrade \
  -r requirements.txt

# 3. Copy application code
echo "📂 Copying application code..."
cp -r app $PACKAGE_DIR/

# 4. Remove unnecessary files to reduce package size
echo "✂️ Removing unnecessary files (__pycache__, etc.)..."
find $PACKAGE_DIR -name "__pycache__" -exec rm -rf {} +
find $PACKAGE_DIR -name "*.dist-info" -exec rm -rf {} +
find $PACKAGE_DIR -name "*.egg-info" -exec rm -rf {} +

# 5. Create the ZIP archive
echo "🤐 Creating ZIP archive: $ZIP_FILE..."
cd $PACKAGE_DIR
zip -q -r ../$ZIP_FILE .
cd ..

echo "✅ Packaging complete! Archive created at: $ZIP_FILE"
echo "📦 Total size: $(du -sh $ZIP_FILE | cut -f1)"
echo "💡 You can now deploy using: aws lambda update-function-code --function-name RetailOpsAgent --zip-file fileb://$ZIP_FILE"
