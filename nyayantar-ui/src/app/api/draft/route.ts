import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      document_type, 
      subject, 
      parties, 
      key_terms, 
      jurisdiction, 
      language, 
      additional_context 
    } = body;

    // Validate required fields
    if (!document_type || typeof document_type !== 'string') {
      return NextResponse.json(
        { error: 'Document type is required and must be a string' },
        { status: 400 }
      );
    }

    if (!subject || typeof subject !== 'string') {
      return NextResponse.json(
        { error: 'Subject is required and must be a string' },
        { status: 400 }
      );
    }

    if (!parties || !Array.isArray(parties)) {
      return NextResponse.json(
        { error: 'Parties is required and must be an array' },
        { status: 400 }
      );
    }

    if (!key_terms || typeof key_terms !== 'object') {
      return NextResponse.json(
        { error: 'Key terms is required and must be an object' },
        { status: 400 }
      );
    }

    console.log('Sending drafting request to backend:', {
      document_type,
      subject,
      parties: parties.length,
      key_terms: Object.keys(key_terms),
      language
    });

    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

    const response = await fetch(`${backendUrl}/api/draft`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        document_type,
        subject,
        parties,
        key_terms,
        jurisdiction: jurisdiction || 'India',
        language: language || 'english',
        additional_context: additional_context || null
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend drafting error:', errorText);
      return NextResponse.json(
        { error: `Backend error: ${response.status} ${response.statusText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in drafting API route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
