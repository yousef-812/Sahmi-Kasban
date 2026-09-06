import 'package:flutter/material.dart';

import '../../features/community/screens/trading_session_chat_screen.dart';

class FloatingTradingRoomButton extends StatefulWidget {
  const FloatingTradingRoomButton({
    super.key,
    this.votesCount = 0,
    this.votesTarget = 40,
  });

  final int votesCount;
  final int votesTarget;

  @override
  State<FloatingTradingRoomButton> createState() =>
      _FloatingTradingRoomButtonState();
}

class _FloatingTradingRoomButtonState extends State<FloatingTradingRoomButton> {
  Offset _position = const Offset(16, 200);

  void _openChatScreen() {
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => const TradingSessionChatScreen(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;

    return Positioned(
      left: _position.dx,
      top: _position.dy,
      child: GestureDetector(
        onPanUpdate: (details) {
          setState(() {
            _position += details.delta;
            _position = Offset(
              _position.dx.clamp(0.0, screenSize.width - 64),
              _position.dy.clamp(50.0, screenSize.height - 120),
            );
          });
        },
        onTap: _openChatScreen,
        child: Material(
          elevation: 6,
          shape: const CircleBorder(),
          color: const Color(0xFF0088CC), // Telegram brand blue
          child: Stack(
            clipBehavior: Clip.none,
            alignment: Alignment.center,
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.send_rounded,
                  color: Colors.white,
                  size: 26,
                ),
              ),
              // Live Votes / Telegram Badge
              Positioned(
                top: -4,
                right: -4,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.amber,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: Colors.white, width: 1.5),
                  ),
                  child: Text(
                    '${widget.votesCount}/${widget.votesTarget}',
                    style: const TextStyle(
                      color: Colors.black,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
