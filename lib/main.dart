import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'utils/constants.dart';
import 'screens/auth/login_screen.dart';
import 'screens/dashboard/user_dashboard.dart';
import 'screens/dashboard/admin_dashboard.dart';
import 'screens/history/history_screen.dart';
import 'screens/profile/profile_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Set status bar color
    SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
    ));

    return MaterialApp(
      title: 'Fire Safety IoT',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primaryColor: kPrimaryColor,
        scaffoldBackgroundColor: kPrimaryColor,
        colorScheme: ColorScheme.dark(
          primary: kPrimaryColor,
          secondary: kAccentColor,
          surface: kSecondaryColor,
        ),
        fontFamily: 'Roboto', // Or any other font you prefer
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.transparent,
          elevation: 0,
          centerTitle: true,
          titleTextStyle: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: kAccentColor,
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white.withValues(alpha: 0.05),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          labelStyle: const TextStyle(color: Colors.white70),
          prefixIconColor: Colors.white70,
        ),
      ),
      home: const LoginScreen(),
    );
  }
}

// --- MAIN LAYOUT (Bottom Nav) ---

class MainLayout extends StatefulWidget {
  final String userEmail;
  final String userName;
  final bool isAdmin;
  const MainLayout({super.key, required this.userEmail, required this.userName, this.isAdmin = false});

  @override
  State<MainLayout> createState() => _MainLayoutState();
}

class _MainLayoutState extends State<MainLayout> {
  int _currentIndex = 0;
  late List<Widget> _screens;

  @override
  void initState() {
    super.initState();
    if (widget.isAdmin) {
       _screens = [
        AdminDashboard(userEmail: widget.userEmail, userName: widget.userName),
        HistoryScreen(userEmail: widget.userEmail), // Admin sees all logs if email is empty, but here we pass admin email? 
        // Actually, AdminDashboard has a button to view logs. 
        // If we use MainLayout for Admin, we should probably have AdminDashboard as Home.
        // And maybe Profile.
        ProfileScreen(userEmail: widget.userEmail, userName: widget.userName),
      ];
    } else {
      _screens = [
        UserDashboard(userEmail: widget.userEmail, userName: widget.userName),
        HistoryScreen(userEmail: widget.userEmail),
        ProfileScreen(userEmail: widget.userEmail, userName: widget.userName),
      ];
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: Container(
        margin: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: kSecondaryColor,
          borderRadius: BorderRadius.circular(30),
          boxShadow: [
            BoxShadow(color: Colors.black.withValues(alpha: 0.3), blurRadius: 20, offset: const Offset(0, 10)),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(30),
          child: BottomNavigationBar(
            currentIndex: _currentIndex,
            onTap: (index) => setState(() => _currentIndex = index),
            backgroundColor: kSecondaryColor,
            selectedItemColor: kAccentColor,
            unselectedItemColor: Colors.white54,
            showSelectedLabels: false,
            showUnselectedLabels: false,
            items: const [
              BottomNavigationBarItem(icon: Icon(Icons.dashboard_rounded), label: 'Home'),
              BottomNavigationBarItem(icon: Icon(Icons.history_rounded), label: 'History'),
              BottomNavigationBarItem(icon: Icon(Icons.person_rounded), label: 'Profile'),
            ],
          ),
        ),
      ),
    );
  }
}
