@description('Main Bicep template for DNB Presentation Generator infrastructure')

// Parameters
@description('Environment name (dev, test, prod)')
@allowed(['dev', 'test', 'prod'])
param environment string = 'dev'

@description('Location for all resources')
param location string = resourceGroup().location

@description('Unique suffix for resource names')
param uniqueSuffix string = uniqueString(resourceGroup().id)

@description('Application name')
param appName string = 'dnb-presentation-generator'

@description('Azure OpenAI configuration')
param azureOpenAI object = {
  location: 'eastus'
  sku: 'S0'
  deployments: [
    {
      name: 'gpt-4o'
      model: 'gpt-4o'
      version: '2024-02-01'
      capacity: 30
    }
  ]
}

// Variables
var resourceNames = {
  containerApp: '${appName}-app-${environment}-${uniqueSuffix}'
  containerAppEnv: '${appName}-env-${environment}-${uniqueSuffix}'
  logAnalytics: '${appName}-logs-${environment}-${uniqueSuffix}'
  appInsights: '${appName}-insights-${environment}-${uniqueSuffix}'
  keyVault: '${appName}-kv-${environment}-${uniqueSuffix}'
  storage: '${appName}storage${environment}${uniqueSuffix}'
  sqlServer: '${appName}-sql-${environment}-${uniqueSuffix}'
  sqlDatabase: '${appName}-db-${environment}'
  redis: '${appName}-redis-${environment}-${uniqueSuffix}'
  cognitiveServices: '${appName}-ai-${environment}-${uniqueSuffix}'
  vnet: '${appName}-vnet-${environment}-${uniqueSuffix}'
  privateEndpoints: '${appName}-pe-${environment}-${uniqueSuffix}'
}

// Virtual Network
module networking 'modules/networking.bicep' = {
  name: 'networking'
  params: {
    vnetName: resourceNames.vnet
    location: location
    environment: environment
  }
}

// Log Analytics Workspace
module logAnalytics 'modules/log-analytics.bicep' = {
  name: 'logAnalytics'
  params: {
    workspaceName: resourceNames.logAnalytics
    location: location
    environment: environment
  }
}

// Application Insights
module appInsights 'modules/app-insights.bicep' = {
  name: 'appInsights'
  params: {
    appInsightsName: resourceNames.appInsights
    location: location
    workspaceId: logAnalytics.outputs.workspaceId
    environment: environment
  }
}

// Key Vault
module keyVault 'modules/key-vault.bicep' = {
  name: 'keyVault'
  params: {
    keyVaultName: resourceNames.keyVault
    location: location
    environment: environment
    subnetId: networking.outputs.privateEndpointSubnetId
  }
}

// Storage Account
module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: {
    storageAccountName: resourceNames.storage
    location: location
    environment: environment
    subnetId: networking.outputs.privateEndpointSubnetId
  }
}

// Azure SQL Database
module sqlDatabase 'modules/sql-database.bicep' = {
  name: 'sqlDatabase'
  params: {
    sqlServerName: resourceNames.sqlServer
    sqlDatabaseName: resourceNames.sqlDatabase
    location: location
    environment: environment
    subnetId: networking.outputs.privateEndpointSubnetId
  }
}

// Azure Cache for Redis
module redis 'modules/redis.bicep' = {
  name: 'redis'
  params: {
    redisName: resourceNames.redis
    location: location
    environment: environment
    subnetId: networking.outputs.privateEndpointSubnetId
  }
}

// Azure Cognitive Services (OpenAI)
module cognitiveServices 'modules/cognitive-services.bicep' = {
  name: 'cognitiveServices'
  params: {
    cognitiveServicesName: resourceNames.cognitiveServices
    location: azureOpenAI.location
    environment: environment
    sku: azureOpenAI.sku
    deployments: azureOpenAI.deployments
    subnetId: networking.outputs.privateEndpointSubnetId
  }
}

// Container App Environment
module containerAppEnv 'modules/container-app-env.bicep' = {
  name: 'containerAppEnv'
  params: {
    containerAppEnvName: resourceNames.containerAppEnv
    location: location
    environment: environment
    logAnalyticsWorkspaceId: logAnalytics.outputs.workspaceId
    subnetId: networking.outputs.containerAppSubnetId
  }
}

// Container App
module containerApp 'modules/container-app.bicep' = {
  name: 'containerApp'
  params: {
    containerAppName: resourceNames.containerApp
    location: location
    environment: environment
    containerAppEnvironmentId: containerAppEnv.outputs.containerAppEnvironmentId
    keyVaultName: keyVault.outputs.keyVaultName
    storageAccountName: storage.outputs.storageAccountName
    sqlConnectionString: sqlDatabase.outputs.connectionString
    redisConnectionString: redis.outputs.connectionString
    cognitiveServicesEndpoint: cognitiveServices.outputs.endpoint
    applicationInsightsConnectionString: appInsights.outputs.connectionString
  }
}

// Outputs
output resourceGroupName string = resourceGroup().name
output containerAppUrl string = containerApp.outputs.containerAppUrl
output keyVaultName string = keyVault.outputs.keyVaultName
output storageAccountName string = storage.outputs.storageAccountName
output cognitiveServicesEndpoint string = cognitiveServices.outputs.endpoint
output applicationInsightsConnectionString string = appInsights.outputs.connectionString

output deploymentInfo object = {
  environment: environment
  location: location
  appName: appName
  uniqueSuffix: uniqueSuffix
  deploymentTime: utcNow()
  resourceNames: resourceNames
}
