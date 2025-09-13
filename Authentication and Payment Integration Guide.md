# Authentication and Payment Integration Guide

**Author:** Manus AI  
**Date:** September 12, 2025  
**Version:** 1.0

## Overview

This document provides comprehensive implementation guidance for integrating multiple authentication providers and payment processing systems into the Bulk Pickup Service mobile application. The implementation covers Google Sign-In, Facebook Login, Apple Sign-In, email/password authentication, and Stripe payment processing with support for subscriptions and one-time payments.

## Authentication Integration Architecture

### Multi-Provider Authentication Strategy

The application implements a unified authentication system that supports multiple identity providers while maintaining a consistent user experience. The architecture follows OAuth 2.0 standards and implements secure token management with JWT-based session handling.

**Core Authentication Components:**

1. **Authentication Service** - Central authentication logic and token management
2. **Provider Adapters** - Specific implementations for each identity provider
3. **Token Manager** - JWT generation, validation, and refresh logic
4. **Session Store** - Secure session persistence and management
5. **User Mapper** - Unified user profile creation from different providers

### Security Implementation

**Token Security:**
- JWT access tokens with 1-hour expiration
- Refresh tokens with 30-day expiration and rotation
- Secure HTTP-only cookies for web sessions
- Platform-specific secure storage for mobile tokens

**Data Protection:**
- Password hashing using bcrypt with salt rounds of 12
- Sensitive data encryption using AES-256
- API rate limiting to prevent brute force attacks
- Multi-factor authentication support for enhanced security

## Google Sign-In Implementation

### Android Implementation

**Dependencies (build.gradle):**
```gradle
implementation 'com.google.android.gms:play-services-auth:20.7.0'
implementation 'com.google.firebase:firebase-auth:22.1.2'
implementation 'androidx.credentials:credentials:1.2.2'
implementation 'androidx.credentials:credentials-play-services-auth:1.2.2'
implementation 'com.google.android.libraries.identity.googleid:googleid:1.1.0'
```

**Configuration Setup:**
```kotlin
// GoogleSignInConfiguration.kt
class GoogleSignInConfiguration {
    companion object {
        fun getGoogleIdOption(context: Context): GetGoogleIdOption {
            return GetGoogleIdOption.Builder()
                .setFilterByAuthorizedAccounts(false)
                .setServerClientId(BuildConfig.GOOGLE_SERVER_CLIENT_ID)
                .setAutoSelectEnabled(true)
                .build()
        }
        
        fun getCredentialRequest(context: Context): GetCredentialRequest {
            return GetCredentialRequest.Builder()
                .addCredentialOption(getGoogleIdOption(context))
                .build()
        }
    }
}
```

**Sign-In Implementation:**
```kotlin
// GoogleSignInManager.kt
class GoogleSignInManager(private val context: Context) {
    private val credentialManager = CredentialManager.create(context)
    
    suspend fun signIn(): Result<GoogleIdTokenCredential> {
        return try {
            val request = GoogleSignInConfiguration.getCredentialRequest(context)
            val result = credentialManager.getCredential(
                request = request,
                context = context as Activity
            )
            
            when (val credential = result.credential) {
                is GoogleIdTokenCredential -> {
                    Result.success(credential)
                }
                else -> {
                    Result.failure(Exception("Unexpected credential type"))
                }
            }
        } catch (e: GetCredentialException) {
            Result.failure(e)
        }
    }
    
    fun handleSignInResult(credential: GoogleIdTokenCredential): GoogleUserInfo {
        return GoogleUserInfo(
            idToken = credential.idToken,
            id = credential.id,
            displayName = credential.displayName,
            givenName = credential.givenName,
            familyName = credential.familyName,
            phoneNumber = credential.phoneNumber,
            profilePictureUri = credential.profilePictureUri
        )
    }
}
```

### iOS Implementation

**Dependencies (Package.swift):**
```swift
dependencies: [
    .package(url: "https://github.com/google/GoogleSignIn-iOS", from: "7.0.0")
]
```

**Configuration Setup:**
```swift
// GoogleSignInConfiguration.swift
import GoogleSignIn

class GoogleSignInConfiguration {
    static func configure() {
        guard let path = Bundle.main.path(forResource: "GoogleService-Info", ofType: "plist"),
              let plist = NSDictionary(contentsOfFile: path),
              let clientId = plist["CLIENT_ID"] as? String else {
            fatalError("GoogleService-Info.plist not found or CLIENT_ID missing")
        }
        
        guard let config = GIDConfiguration(clientID: clientId) else {
            fatalError("Failed to create GIDConfiguration")
        }
        
        GIDSignIn.sharedInstance.configuration = config
    }
}
```

**Sign-In Implementation:**
```swift
// GoogleSignInManager.swift
import GoogleSignIn
import UIKit

class GoogleSignInManager {
    static let shared = GoogleSignInManager()
    
    private init() {}
    
    func signIn(presentingViewController: UIViewController) async throws -> GIDGoogleUser {
        return try await withCheckedThrowingContinuation { continuation in
            GIDSignIn.sharedInstance.signIn(withPresenting: presentingViewController) { result, error in
                if let error = error {
                    continuation.resume(throwing: error)
                } else if let result = result {
                    continuation.resume(returning: result.user)
                } else {
                    continuation.resume(throwing: GoogleSignInError.unknownError)
                }
            }
        }
    }
    
    func handleSignInResult(_ user: GIDGoogleUser) -> GoogleUserInfo {
        return GoogleUserInfo(
            idToken: user.idToken?.tokenString ?? "",
            accessToken: user.accessToken.tokenString,
            userID: user.userID ?? "",
            email: user.profile?.email ?? "",
            fullName: user.profile?.name ?? "",
            givenName: user.profile?.givenName ?? "",
            familyName: user.profile?.familyName ?? "",
            profileImageURL: user.profile?.imageURL(withDimension: 200)?.absoluteString
        )
    }
}

enum GoogleSignInError: Error {
    case unknownError
    case userCancelled
    case configurationError
}
```

### React Native Integration

**Dependencies (package.json):**
```json
{
  "@react-native-google-signin/google-signin": "^10.1.0",
  "@react-native-async-storage/async-storage": "^1.19.3"
}
```

**Configuration and Implementation:**
```typescript
// GoogleSignInService.ts
import { GoogleSignin, statusCodes } from '@react-native-google-signin/google-signin';

export interface GoogleUserInfo {
  idToken: string;
  accessToken: string;
  user: {
    id: string;
    email: string;
    name: string;
    givenName: string;
    familyName: string;
    photo?: string;
  };
}

class GoogleSignInService {
  static async configure(): Promise<void> {
    GoogleSignin.configure({
      webClientId: 'YOUR_WEB_CLIENT_ID',
      offlineAccess: true,
      hostedDomain: '',
      forceCodeForRefreshToken: true,
    });
  }

  static async signIn(): Promise<GoogleUserInfo> {
    try {
      await GoogleSignin.hasPlayServices();
      const userInfo = await GoogleSignin.signIn();
      const tokens = await GoogleSignin.getTokens();
      
      return {
        idToken: tokens.idToken,
        accessToken: tokens.accessToken,
        user: {
          id: userInfo.user.id,
          email: userInfo.user.email,
          name: userInfo.user.name || '',
          givenName: userInfo.user.givenName || '',
          familyName: userInfo.user.familyName || '',
          photo: userInfo.user.photo || undefined,
        },
      };
    } catch (error: any) {
      if (error.code === statusCodes.SIGN_IN_CANCELLED) {
        throw new Error('User cancelled sign in');
      } else if (error.code === statusCodes.IN_PROGRESS) {
        throw new Error('Sign in already in progress');
      } else if (error.code === statusCodes.PLAY_SERVICES_NOT_AVAILABLE) {
        throw new Error('Play services not available');
      } else {
        throw new Error(`Google Sign In failed: ${error.message}`);
      }
    }
  }

  static async signOut(): Promise<void> {
    try {
      await GoogleSignin.signOut();
    } catch (error) {
      console.error('Google Sign Out error:', error);
    }
  }

  static async isSignedIn(): Promise<boolean> {
    return GoogleSignin.isSignedIn();
  }
}

export default GoogleSignInService;
```

## Facebook Login Implementation

### Android Implementation

**Dependencies (build.gradle):**
```gradle
implementation 'com.facebook.android:facebook-login:16.2.0'
implementation 'com.facebook.android:facebook-android-sdk:16.2.0'
```

**Configuration Setup:**
```kotlin
// FacebookConfiguration.kt
import com.facebook.FacebookSdk
import com.facebook.appevents.AppEventsLogger

class FacebookConfiguration {
    companion object {
        fun initialize(context: Context) {
            FacebookSdk.sdkInitialize(context)
            AppEventsLogger.activateApp(context as Application)
        }
    }
}
```

**Login Implementation:**
```kotlin
// FacebookLoginManager.kt
import com.facebook.CallbackManager
import com.facebook.FacebookCallback
import com.facebook.FacebookException
import com.facebook.login.LoginManager
import com.facebook.login.LoginResult
import com.facebook.GraphRequest
import org.json.JSONObject

class FacebookLoginManager(private val activity: Activity) {
    private val callbackManager = CallbackManager.Factory.create()
    private val loginManager = LoginManager.getInstance()
    
    fun login(callback: (Result<FacebookUserInfo>) -> Unit) {
        loginManager.registerCallback(callbackManager, object : FacebookCallback<LoginResult> {
            override fun onSuccess(result: LoginResult) {
                fetchUserProfile(result.accessToken.token) { userInfo ->
                    callback(Result.success(userInfo))
                }
            }
            
            override fun onCancel() {
                callback(Result.failure(Exception("User cancelled Facebook login")))
            }
            
            override fun onError(error: FacebookException) {
                callback(Result.failure(error))
            }
        })
        
        loginManager.logInWithReadPermissions(
            activity,
            listOf("email", "public_profile")
        )
    }
    
    private fun fetchUserProfile(accessToken: String, callback: (FacebookUserInfo) -> Unit) {
        val request = GraphRequest.newMeRequest(
            com.facebook.AccessToken.getCurrentAccessToken()
        ) { jsonObject, _ ->
            val userInfo = parseFacebookUser(jsonObject, accessToken)
            callback(userInfo)
        }
        
        val parameters = Bundle()
        parameters.putString("fields", "id,name,email,first_name,last_name,picture.type(large)")
        request.parameters = parameters
        request.executeAsync()
    }
    
    private fun parseFacebookUser(jsonObject: JSONObject?, accessToken: String): FacebookUserInfo {
        return FacebookUserInfo(
            accessToken = accessToken,
            id = jsonObject?.getString("id") ?: "",
            email = jsonObject?.optString("email") ?: "",
            name = jsonObject?.optString("name") ?: "",
            firstName = jsonObject?.optString("first_name") ?: "",
            lastName = jsonObject?.optString("last_name") ?: "",
            profilePictureUrl = jsonObject?.optJSONObject("picture")
                ?.optJSONObject("data")
                ?.optString("url")
        )
    }
    
    fun handleActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        callbackManager.onActivityResult(requestCode, resultCode, data)
    }
}
```

### iOS Implementation

**Dependencies (Package.swift):**
```swift
dependencies: [
    .package(url: "https://github.com/facebook/facebook-ios-sdk", from: "16.2.0")
]
```

**Configuration and Implementation:**
```swift
// FacebookLoginManager.swift
import FBSDKLoginKit
import FBSDKCoreKit

class FacebookLoginManager {
    static let shared = FacebookLoginManager()
    private let loginManager = LoginManager()
    
    private init() {}
    
    func login(from viewController: UIViewController) async throws -> FacebookUserInfo {
        return try await withCheckedThrowingContinuation { continuation in
            loginManager.logIn(permissions: ["email", "public_profile"], from: viewController) { result, error in
                if let error = error {
                    continuation.resume(throwing: error)
                } else if let result = result {
                    if result.isCancelled {
                        continuation.resume(throwing: FacebookLoginError.userCancelled)
                    } else {
                        Task {
                            do {
                                let userInfo = try await self.fetchUserProfile(token: result.token?.tokenString ?? "")
                                continuation.resume(returning: userInfo)
                            } catch {
                                continuation.resume(throwing: error)
                            }
                        }
                    }
                } else {
                    continuation.resume(throwing: FacebookLoginError.unknownError)
                }
            }
        }
    }
    
    private func fetchUserProfile(token: String) async throws -> FacebookUserInfo {
        return try await withCheckedThrowingContinuation { continuation in
            let request = GraphRequest(graphPath: "me", parameters: [
                "fields": "id,name,email,first_name,last_name,picture.type(large)"
            ])
            
            request.start { _, result, error in
                if let error = error {
                    continuation.resume(throwing: error)
                } else if let result = result as? [String: Any] {
                    let userInfo = FacebookUserInfo(
                        accessToken: token,
                        id: result["id"] as? String ?? "",
                        email: result["email"] as? String ?? "",
                        name: result["name"] as? String ?? "",
                        firstName: result["first_name"] as? String ?? "",
                        lastName: result["last_name"] as? String ?? "",
                        profilePictureUrl: (result["picture"] as? [String: Any])?["data"] as? [String: Any])?["url"] as? String
                    )
                    continuation.resume(returning: userInfo)
                } else {
                    continuation.resume(throwing: FacebookLoginError.invalidResponse)
                }
            }
        }
    }
    
    func logout() {
        loginManager.logOut()
    }
}

enum FacebookLoginError: Error {
    case userCancelled
    case unknownError
    case invalidResponse
}
```

## Apple Sign-In Implementation

### iOS Implementation

**Configuration and Implementation:**
```swift
// AppleSignInManager.swift
import AuthenticationServices
import CryptoKit

class AppleSignInManager: NSObject {
    static let shared = AppleSignInManager()
    private var currentNonce: String?
    
    private override init() {
        super.init()
    }
    
    func signIn() async throws -> AppleUserInfo {
        return try await withCheckedThrowingContinuation { continuation in
            let nonce = randomNonceString()
            currentNonce = nonce
            
            let appleIDProvider = ASAuthorizationAppleIDProvider()
            let request = appleIDProvider.createRequest()
            request.requestedScopes = [.fullName, .email]
            request.nonce = sha256(nonce)
            
            let authorizationController = ASAuthorizationController(authorizationRequests: [request])
            authorizationController.delegate = self
            authorizationController.presentationContextProvider = self
            authorizationController.performRequests()
            
            self.signInContinuation = continuation
        }
    }
    
    private var signInContinuation: CheckedContinuation<AppleUserInfo, Error>?
    
    private func randomNonceString(length: Int = 32) -> String {
        precondition(length > 0)
        let charset: [Character] = Array("0123456789ABCDEFGHIJKLMNOPQRSTUVXYZabcdefghijklmnopqrstuvwxyz-._")
        var result = ""
        var remainingLength = length
        
        while remainingLength > 0 {
            let randoms: [UInt8] = (0 ..< 16).map { _ in
                var random: UInt8 = 0
                let errorCode = SecRandomCopyBytes(kSecRandomDefault, 1, &random)
                if errorCode != errSecSuccess {
                    fatalError("Unable to generate nonce. SecRandomCopyBytes failed with OSStatus \(errorCode)")
                }
                return random
            }
            
            randoms.forEach { random in
                if remainingLength == 0 {
                    return
                }
                
                if random < charset.count {
                    result.append(charset[Int(random)])
                    remainingLength -= 1
                }
            }
        }
        
        return result
    }
    
    private func sha256(_ input: String) -> String {
        let inputData = Data(input.utf8)
        let hashedData = SHA256.hash(data: inputData)
        let hashString = hashedData.compactMap {
            String(format: "%02x", $0)
        }.joined()
        
        return hashString
    }
}

extension AppleSignInManager: ASAuthorizationControllerDelegate {
    func authorizationController(controller: ASAuthorizationController, didCompleteWithAuthorization authorization: ASAuthorization) {
        if let appleIDCredential = authorization.credential as? ASAuthorizationAppleIDCredential {
            guard let nonce = currentNonce else {
                signInContinuation?.resume(throwing: AppleSignInError.invalidState)
                return
            }
            
            guard let appleIDToken = appleIDCredential.identityToken else {
                signInContinuation?.resume(throwing: AppleSignInError.invalidCredential)
                return
            }
            
            guard let idTokenString = String(data: appleIDToken, encoding: .utf8) else {
                signInContinuation?.resume(throwing: AppleSignInError.invalidToken)
                return
            }
            
            let userInfo = AppleUserInfo(
                identityToken: idTokenString,
                authorizationCode: String(data: appleIDCredential.authorizationCode ?? Data(), encoding: .utf8) ?? "",
                userIdentifier: appleIDCredential.user,
                email: appleIDCredential.email,
                fullName: appleIDCredential.fullName,
                realUserStatus: appleIDCredential.realUserStatus
            )
            
            signInContinuation?.resume(returning: userInfo)
        } else {
            signInContinuation?.resume(throwing: AppleSignInError.invalidCredential)
        }
    }
    
    func authorizationController(controller: ASAuthorizationController, didCompleteWithError error: Error) {
        signInContinuation?.resume(throwing: error)
    }
}

extension AppleSignInManager: ASAuthorizationControllerPresentationContextProviding {
    func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor {
        return UIApplication.shared.windows.first { $0.isKeyWindow } ?? UIWindow()
    }
}

enum AppleSignInError: Error {
    case invalidState
    case invalidCredential
    case invalidToken
}
```

### Android Implementation

**Dependencies (build.gradle):**
```gradle
implementation 'com.willowtreeapps:sign-in-with-apple-button-android:0.3'
```

**Implementation:**
```kotlin
// AppleSignInManager.kt
import com.willowtreeapps.signinwithapplebutton.SignInWithAppleButton
import com.willowtreeapps.signinwithapplebutton.SignInWithAppleConfiguration
import com.willowtreeapps.signinwithapplebutton.SignInWithAppleResult

class AppleSignInManager(private val activity: Activity) {
    
    fun signIn(callback: (Result<AppleUserInfo>) -> Unit) {
        val configuration = SignInWithAppleConfiguration.Builder()
            .clientId("your.app.bundle.id")
            .redirectUri("https://your-backend.com/auth/apple/callback")
            .scope("email name")
            .build()
        
        SignInWithAppleButton.signIn(activity, configuration) { result ->
            when (result) {
                is SignInWithAppleResult.Success -> {
                    val userInfo = AppleUserInfo(
                        identityToken = result.identityToken,
                        authorizationCode = result.authorizationCode,
                        userIdentifier = result.user,
                        email = result.email,
                        fullName = "${result.firstName ?: ""} ${result.lastName ?: ""}".trim(),
                        firstName = result.firstName,
                        lastName = result.lastName
                    )
                    callback(Result.success(userInfo))
                }
                is SignInWithAppleResult.Failure -> {
                    callback(Result.failure(Exception(result.error.localizedMessage)))
                }
                is SignInWithAppleResult.Cancel -> {
                    callback(Result.failure(Exception("User cancelled Apple Sign In")))
                }
            }
        }
    }
}
```

## Email/Password Authentication Implementation

### Firebase Authentication Integration

**Dependencies:**
```json
{
  "@react-native-firebase/app": "^18.5.0",
  "@react-native-firebase/auth": "^18.5.0"
}
```

**Implementation:**
```typescript
// EmailPasswordAuthService.ts
import auth, { FirebaseAuthTypes } from '@react-native-firebase/auth';

export interface EmailPasswordCredentials {
  email: string;
  password: string;
}

export interface UserRegistrationData extends EmailPasswordCredentials {
  firstName: string;
  lastName: string;
  userType: 'resident' | 'business';
  phoneNumber?: string;
}

class EmailPasswordAuthService {
  static async register(userData: UserRegistrationData): Promise<FirebaseAuthTypes.UserCredential> {
    try {
      const userCredential = await auth().createUserWithEmailAndPassword(
        userData.email,
        userData.password
      );
      
      // Update user profile
      await userCredential.user.updateProfile({
        displayName: `${userData.firstName} ${userData.lastName}`,
      });
      
      // Send email verification
      await userCredential.user.sendEmailVerification();
      
      return userCredential;
    } catch (error: any) {
      throw this.handleAuthError(error);
    }
  }
  
  static async signIn(credentials: EmailPasswordCredentials): Promise<FirebaseAuthTypes.UserCredential> {
    try {
      return await auth().signInWithEmailAndPassword(
        credentials.email,
        credentials.password
      );
    } catch (error: any) {
      throw this.handleAuthError(error);
    }
  }
  
  static async signOut(): Promise<void> {
    try {
      await auth().signOut();
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  }
  
  static async resetPassword(email: string): Promise<void> {
    try {
      await auth().sendPasswordResetEmail(email);
    } catch (error: any) {
      throw this.handleAuthError(error);
    }
  }
  
  static async updatePassword(newPassword: string): Promise<void> {
    try {
      const user = auth().currentUser;
      if (!user) {
        throw new Error('No authenticated user');
      }
      
      await user.updatePassword(newPassword);
    } catch (error: any) {
      throw this.handleAuthError(error);
    }
  }
  
  static async sendEmailVerification(): Promise<void> {
    try {
      const user = auth().currentUser;
      if (!user) {
        throw new Error('No authenticated user');
      }
      
      await user.sendEmailVerification();
    } catch (error: any) {
      throw this.handleAuthError(error);
    }
  }
  
  static async reauthenticate(password: string): Promise<void> {
    try {
      const user = auth().currentUser;
      if (!user || !user.email) {
        throw new Error('No authenticated user');
      }
      
      const credential = auth.EmailAuthProvider.credential(user.email, password);
      await user.reauthenticateWithCredential(credential);
    } catch (error: any) {
      throw this.handleAuthError(error);
    }
  }
  
  private static handleAuthError(error: any): Error {
    switch (error.code) {
      case 'auth/email-already-in-use':
        return new Error('An account with this email already exists');
      case 'auth/invalid-email':
        return new Error('Invalid email address');
      case 'auth/weak-password':
        return new Error('Password is too weak');
      case 'auth/user-not-found':
        return new Error('No account found with this email');
      case 'auth/wrong-password':
        return new Error('Incorrect password');
      case 'auth/too-many-requests':
        return new Error('Too many failed attempts. Please try again later');
      case 'auth/network-request-failed':
        return new Error('Network error. Please check your connection');
      default:
        return new Error(error.message || 'Authentication failed');
    }
  }
  
  static getCurrentUser(): FirebaseAuthTypes.User | null {
    return auth().currentUser;
  }
  
  static onAuthStateChanged(callback: (user: FirebaseAuthTypes.User | null) => void): () => void {
    return auth().onAuthStateChanged(callback);
  }
}

export default EmailPasswordAuthService;
```

### Password Validation

**Implementation:**
```typescript
// PasswordValidator.ts
export interface PasswordValidationResult {
  isValid: boolean;
  errors: string[];
  strength: 'weak' | 'medium' | 'strong';
}

class PasswordValidator {
  private static readonly MIN_LENGTH = 8;
  private static readonly MAX_LENGTH = 128;
  
  static validate(password: string): PasswordValidationResult {
    const errors: string[] = [];
    
    // Length validation
    if (password.length < this.MIN_LENGTH) {
      errors.push(`Password must be at least ${this.MIN_LENGTH} characters long`);
    }
    
    if (password.length > this.MAX_LENGTH) {
      errors.push(`Password must be no more than ${this.MAX_LENGTH} characters long`);
    }
    
    // Character type validation
    if (!/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }
    
    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }
    
    if (!/\d/.test(password)) {
      errors.push('Password must contain at least one number');
    }
    
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
      errors.push('Password must contain at least one special character');
    }
    
    // Common password check
    if (this.isCommonPassword(password)) {
      errors.push('Password is too common. Please choose a more unique password');
    }
    
    const strength = this.calculateStrength(password);
    
    return {
      isValid: errors.length === 0,
      errors,
      strength,
    };
  }
  
  private static calculateStrength(password: string): 'weak' | 'medium' | 'strong' {
    let score = 0;
    
    // Length bonus
    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 1;
    if (password.length >= 16) score += 1;
    
    // Character variety bonus
    if (/[a-z]/.test(password)) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/\d/.test(password)) score += 1;
    if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) score += 1;
    
    // Pattern bonus
    if (!/(.)\1{2,}/.test(password)) score += 1; // No repeated characters
    if (!/123|abc|qwe/i.test(password)) score += 1; // No sequential patterns
    
    if (score <= 3) return 'weak';
    if (score <= 6) return 'medium';
    return 'strong';
  }
  
  private static isCommonPassword(password: string): boolean {
    const commonPasswords = [
      'password', '123456', '123456789', 'qwerty', 'abc123',
      'password123', 'admin', 'letmein', 'welcome', 'monkey'
    ];
    
    return commonPasswords.includes(password.toLowerCase());
  }
}

export default PasswordValidator;
```

## Stripe Payment Integration

### Mobile SDK Setup

**React Native Dependencies:**
```json
{
  "@stripe/stripe-react-native": "^0.35.0",
  "@stripe/stripe-js": "^2.1.11"
}
```

**Stripe Provider Setup:**
```typescript
// StripeProvider.tsx
import React from 'react';
import { StripeProvider as StripeProviderNative } from '@stripe/stripe-react-native';

interface StripeProviderProps {
  children: React.ReactNode;
}

const StripeProvider: React.FC<StripeProviderProps> = ({ children }) => {
  return (
    <StripeProviderNative
      publishableKey="pk_test_your_publishable_key"
      merchantIdentifier="merchant.com.yourapp.bulkpickup"
      urlScheme="your-app-scheme"
    >
      {children}
    </StripeProviderNative>
  );
};

export default StripeProvider;
```

### Payment Methods Management

**Implementation:**
```typescript
// PaymentMethodService.ts
import { useStripe, useConfirmPayment } from '@stripe/stripe-react-native';

export interface PaymentMethod {
  id: string;
  type: 'card' | 'apple_pay' | 'google_pay';
  card?: {
    brand: string;
    last4: string;
    expMonth: number;
    expYear: number;
  };
  isDefault: boolean;
}

export interface SetupIntentResult {
  setupIntent: {
    id: string;
    clientSecret: string;
    status: string;
  };
  paymentMethod?: PaymentMethod;
}

class PaymentMethodService {
  private stripe: any;
  
  constructor() {
    this.stripe = useStripe();
  }
  
  async createSetupIntent(): Promise<string> {
    try {
      const response = await fetch('/api/payments/setup-intent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await this.getAuthToken()}`,
        },
      });
      
      const { clientSecret } = await response.json();
      return clientSecret;
    } catch (error) {
      throw new Error('Failed to create setup intent');
    }
  }
  
  async confirmSetupIntent(clientSecret: string, paymentMethodData: any): Promise<SetupIntentResult> {
    try {
      const { setupIntent, error } = await this.stripe.confirmSetupIntent(clientSecret, {
        paymentMethodType: 'Card',
        paymentMethodData,
      });
      
      if (error) {
        throw new Error(error.message);
      }
      
      return { setupIntent };
    } catch (error: any) {
      throw new Error(`Setup intent confirmation failed: ${error.message}`);
    }
  }
  
  async getPaymentMethods(): Promise<PaymentMethod[]> {
    try {
      const response = await fetch('/api/payments/methods', {
        headers: {
          'Authorization': `Bearer ${await this.getAuthToken()}`,
        },
      });
      
      const { paymentMethods } = await response.json();
      return paymentMethods;
    } catch (error) {
      throw new Error('Failed to fetch payment methods');
    }
  }
  
  async deletePaymentMethod(paymentMethodId: string): Promise<void> {
    try {
      const response = await fetch(`/api/payments/methods/${paymentMethodId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${await this.getAuthToken()}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete payment method');
      }
    } catch (error) {
      throw new Error('Failed to delete payment method');
    }
  }
  
  async setDefaultPaymentMethod(paymentMethodId: string): Promise<void> {
    try {
      const response = await fetch(`/api/payments/methods/${paymentMethodId}/default`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${await this.getAuthToken()}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to set default payment method');
      }
    } catch (error) {
      throw new Error('Failed to set default payment method');
    }
  }
  
  private async getAuthToken(): Promise<string> {
    // Implementation depends on your auth system
    // Return the current user's JWT token
    return 'jwt_token_here';
  }
}

export default PaymentMethodService;
```

### Subscription Management

**Implementation:**
```typescript
// SubscriptionService.ts
export interface SubscriptionPlan {
  id: string;
  name: string;
  description: string;
  price: number;
  currency: string;
  interval: 'month' | 'year';
  features: string[];
}

export interface Subscription {
  id: string;
  planId: string;
  status: 'active' | 'canceled' | 'past_due' | 'unpaid';
  currentPeriodStart: string;
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
}

class SubscriptionService {
  async getAvailablePlans(): Promise<SubscriptionPlan[]> {
    try {
      const response = await fetch('/api/subscriptions/plans', {
        headers: {
          'Authorization': `Bearer ${await this.getAuthToken()}`,
        },
      });
      
      const { plans } = await response.json();
      return plans;
    } catch (error) {
      throw new Error('Failed to fetch subscription plans');
    }
  }
  
  async getCurrentSubscription(): Promise<Subscription | null> {
    try {
      const response = await fetch('/api/subscriptions/current', {
        headers: {
          'Authorization': `Bearer ${await this.getAuthToken()}`,
        },
      });
      
      if (response.status === 404) {
        return null; // No active subscription
      }
      
      const { subscription } = await response.json();
      return subscription;
    } catch (error) {
      throw new Error('Failed to fetch current subscription');
    }
  }
  
  async createSubscription(planId: string, paymentMethodId: string): Promise<Subscription> {
    try {
      const response = await fetch('/api/subscriptions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await this.getAuthToken()}`,
        },
        body: JSON.stringify({
          planId,
          paymentMethodId,
        }),
      });
      
      const { subscription } = await response.json();
      return subscription;
    } catch (error) {
      throw new Error('Failed to create subscription');
    }
  }
  
  async updateSubscription(subscriptionId: string, newPlanId: string): Promise<Subscription> {
    try {
      const response = await fetch(`/api/subscriptions/${subscriptionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await this.getAuthToken()}`,
        },
        body: JSON.stringify({
          planId: newPlanId,
        }),
      });
      
      const { subscription } = await response.json();
      return subscription;
    } catch (error) {
      throw new Error('Failed to update subscription');
    }
  }
  
  async cancelSubscription(subscriptionId: string, cancelAtPeriodEnd: boolean = true): Promise<Subscription> {
    try {
      const response = await fetch(`/api/subscriptions/${subscriptionId}/cancel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await this.getAuthToken()}`,
        },
        body: JSON.stringify({
          cancelAtPeriodEnd,
        }),
      });
      
      const { subscription } = await response.json();
      return subscription;
    } catch (error) {
      throw new Error('Failed to cancel subscription');
    }
  }
  
  async reactivateSubscription(subscriptionId: string): Promise<Subscription> {
    try {
      const response = await fetch(`/api/subscriptions/${subscriptionId}/reactivate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${await this.getAuthToken()}`,
        },
      });
      
      const { subscription } = await response.json();
      return subscription;
    } catch (error) {
      throw new Error('Failed to reactivate subscription');
    }
  }
  
  private async getAuthToken(): Promise<string> {
    // Implementation depends on your auth system
    return 'jwt_token_here';
  }
}

export default SubscriptionService;
```

### One-Time Payment Processing

**Implementation:**
```typescript
// PaymentService.ts
import { useStripe, useConfirmPayment } from '@stripe/stripe-react-native';

export interface PaymentIntentData {
  amount: number;
  currency: string;
  description: string;
  metadata?: Record<string, string>;
}

export interface PaymentResult {
  paymentIntent: {
    id: string;
    status: string;
    amount: number;
    currency: string;
  };
  error?: string;
}

class PaymentService {
  private stripe: any;
  private confirmPayment: any;
  
  constructor() {
    this.stripe = useStripe();
    this.confirmPayment = useConfirmPayment();
  }
  
  async createPaymentIntent(data: PaymentIntentData): Promise<string> {
    try {
      const response = await fetch('/api/payments/payment-intent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await this.getAuthToken()}`,
        },
        body: JSON.stringify(data),
      });
      
      const { clientSecret } = await response.json();
      return clientSecret;
    } catch (error) {
      throw new Error('Failed to create payment intent');
    }
  }
  
  async confirmCardPayment(
    clientSecret: string,
    paymentMethodData: any
  ): Promise<PaymentResult> {
    try {
      const { paymentIntent, error } = await this.confirmPayment(clientSecret, {
        paymentMethodType: 'Card',
        paymentMethodData,
      });
      
      if (error) {
        return {
          paymentIntent: paymentIntent || {},
          error: error.message,
        };
      }
      
      return { paymentIntent };
    } catch (error: any) {
      throw new Error(`Payment confirmation failed: ${error.message}`);
    }
  }
  
  async confirmApplePayPayment(clientSecret: string): Promise<PaymentResult> {
    try {
      const { paymentIntent, error } = await this.stripe.confirmPayment(clientSecret, {
        paymentMethodType: 'ApplePay',
      });
      
      if (error) {
        return {
          paymentIntent: paymentIntent || {},
          error: error.message,
        };
      }
      
      return { paymentIntent };
    } catch (error: any) {
      throw new Error(`Apple Pay confirmation failed: ${error.message}`);
    }
  }
  
  async confirmGooglePayPayment(clientSecret: string): Promise<PaymentResult> {
    try {
      const { paymentIntent, error } = await this.stripe.confirmPayment(clientSecret, {
        paymentMethodType: 'GooglePay',
      });
      
      if (error) {
        return {
          paymentIntent: paymentIntent || {},
          error: error.message,
        };
      }
      
      return { paymentIntent };
    } catch (error: any) {
      throw new Error(`Google Pay confirmation failed: ${error.message}`);
    }
  }
  
  async getPaymentHistory(limit: number = 20, offset: number = 0): Promise<PaymentResult[]> {
    try {
      const response = await fetch(`/api/payments/history?limit=${limit}&offset=${offset}`, {
        headers: {
          'Authorization': `Bearer ${await this.getAuthToken()}`,
        },
      });
      
      const { payments } = await response.json();
      return payments;
    } catch (error) {
      throw new Error('Failed to fetch payment history');
    }
  }
  
  private async getAuthToken(): Promise<string> {
    // Implementation depends on your auth system
    return 'jwt_token_here';
  }
}

export default PaymentService;
```

## Security Best Practices

### Token Management

**Secure Token Storage:**
```typescript
// SecureTokenStorage.ts
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Keychain from 'react-native-keychain';

class SecureTokenStorage {
  private static readonly ACCESS_TOKEN_KEY = 'access_token';
  private static readonly REFRESH_TOKEN_KEY = 'refresh_token';
  
  static async storeTokens(accessToken: string, refreshToken: string): Promise<void> {
    try {
      // Store access token in memory/AsyncStorage (less sensitive)
      await AsyncStorage.setItem(this.ACCESS_TOKEN_KEY, accessToken);
      
      // Store refresh token in Keychain (more secure)
      await Keychain.setInternetCredentials(
        this.REFRESH_TOKEN_KEY,
        'refresh_token',
        refreshToken
      );
    } catch (error) {
      throw new Error('Failed to store authentication tokens');
    }
  }
  
  static async getAccessToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(this.ACCESS_TOKEN_KEY);
    } catch (error) {
      return null;
    }
  }
  
  static async getRefreshToken(): Promise<string | null> {
    try {
      const credentials = await Keychain.getInternetCredentials(this.REFRESH_TOKEN_KEY);
      if (credentials) {
        return credentials.password;
      }
      return null;
    } catch (error) {
      return null;
    }
  }
  
  static async clearTokens(): Promise<void> {
    try {
      await AsyncStorage.removeItem(this.ACCESS_TOKEN_KEY);
      await Keychain.resetInternetCredentials(this.REFRESH_TOKEN_KEY);
    } catch (error) {
      console.error('Failed to clear tokens:', error);
    }
  }
  
  static async refreshAccessToken(): Promise<string | null> {
    try {
      const refreshToken = await this.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refreshToken }),
      });
      
      if (!response.ok) {
        throw new Error('Token refresh failed');
      }
      
      const { accessToken, refreshToken: newRefreshToken } = await response.json();
      
      await this.storeTokens(accessToken, newRefreshToken);
      return accessToken;
    } catch (error) {
      await this.clearTokens();
      throw error;
    }
  }
}

export default SecureTokenStorage;
```

### API Request Interceptor

**Implementation:**
```typescript
// ApiClient.ts
import SecureTokenStorage from './SecureTokenStorage';

class ApiClient {
  private baseURL: string;
  private isRefreshing: boolean = false;
  private refreshPromise: Promise<string> | null = null;
  
  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }
  
  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const token = await SecureTokenStorage.getAccessToken();
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    let response = await fetch(url, {
      ...options,
      headers,
    });
    
    // Handle token refresh on 401
    if (response.status === 401 && token) {
      const newToken = await this.handleTokenRefresh();
      if (newToken) {
        headers['Authorization'] = `Bearer ${newToken}`;
        response = await fetch(url, {
          ...options,
          headers,
        });
      }
    }
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Request failed' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }
    
    return response.json();
  }
  
  private async handleTokenRefresh(): Promise<string | null> {
    if (this.isRefreshing) {
      return this.refreshPromise;
    }
    
    this.isRefreshing = true;
    this.refreshPromise = SecureTokenStorage.refreshAccessToken();
    
    try {
      const newToken = await this.refreshPromise;
      return newToken;
    } catch (error) {
      // Redirect to login or handle auth failure
      throw error;
    } finally {
      this.isRefreshing = false;
      this.refreshPromise = null;
    }
  }
  
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }
  
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }
  
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }
  
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export default ApiClient;
```

This comprehensive authentication and payment integration guide provides the foundation for implementing secure, scalable authentication and payment processing in the Bulk Pickup Service mobile application. The implementation covers all major authentication providers and payment methods while maintaining security best practices and user experience standards.

