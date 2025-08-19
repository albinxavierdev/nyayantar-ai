import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, chatHistory, feature, language, image_url, document_url } = body;

    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { error: 'Message is required and must be a string' },
        { status: 400 }
      );
    }

    if (!chatHistory || !Array.isArray(chatHistory)) {
      return NextResponse.json(
        { error: 'Chat history is required and must be an array' },
        { status: 400 }
      );
    }

    console.log('Sending request to backend:', { 
      message, 
      chatHistory: chatHistory.length, 
      feature, 
      language,
      hasImage: !!image_url,
      hasDocument: !!document_url
    });

    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

    const response = await fetch(`${backendUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        chatHistory,
        feature: feature || 'chat',
        language: language || 'english',
        image_url: image_url || null,
        document_url: document_url || null
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error:', errorText);
      return NextResponse.json(
        { error: `Backend error: ${response.status} ${response.statusText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in chat API route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
