/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef } from 'react';
import { 
  Folder, 
  FolderOpen, 
  File, 
  ChevronRight, 
  ChevronDown, 
  Terminal, 
  Play, 
  Search, 
  Database, 
  ShieldCheck, 
  Cpu, 
  CheckCircle2, 
  ExternalLink, 
  Copy, 
  Github, 
  GitBranch, 
  Sparkles, 
  Lock, 
  CreditCard,
  Check,
  RefreshCw,
  HelpCircle,
  AlertCircle,
  MessageSquare,
  Sliders,
  User,
  Bot,
  Send,
  Layers,
  Server,
  Fingerprint
} from 'lucide-react';
import { REPO_FILES, REPO_TREE, MOCK_RAG_DATABASE, FolderNode, RepoFile } from './data';
import { motion, AnimatePresence } from 'motion/react';

// Simple custom syntax highlighting using regex replacement
function highlightCode(code: string, language: string) {
  if (language === 'json') {
    return code
      .replace(/(".*?"\s*:)/g, '<span class="text-emerald-400 font-semibold">$1</span>')
      .replace(/(:\s*".*?")/g, ':<span class="text-amber-300">$1</span>')
      .replace(/(:\s*[0-9.]+)/g, ':<span class="text-sky-400">$1</span>');
  }
  if (language === 'python') {
    return code
      .replace(/\b(def|class|import|from|as|return|async|await|pass|yield|for|in|if|else|try|except|with|None|True|False)\b/g, '<span class="text-sky-400 font-medium">$1</span>')
      .replace(/(\".*?\")/g, '<span class="text-amber-200">$1</span>')
      .replace(/(\#.*?)$/gm, '<span class="text-slate-500 italic">$1</span>')
      .replace(/(@\w+)/g, '<span class="text-violet-400">$1</span>');
  }
  if (language === 'markdown') {
    return code
      .replace(/^(#+ .*)$/gm, '<span class="text-emerald-400 font-bold">$1</span>')
      .replace(/(\**.*?\**)/g, '<span class="text-sky-300 font-semibold">$1</span>')
      .replace(/(\`.*?\`)/g, '<span class="text-slate-300 font-mono bg-slate-800/60 px-1 rounded">$1</span>');
  }
  return code;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'explorer' | 'simulator' | 'rag' | 'docs' | 'providers'>('simulator');
  const [selectedFile, setSelectedFile] = useState<RepoFile | null>(REPO_FILES['README.md']);
  const [expandedFolders, setExpandedFolders] = useState<Record<string, boolean>>({
    'hospitality-reservation-payment-agent': true,
    'app': true,
    'app/api': true,
    'graph': true,
    'crew': true,
    'agent_mcp': true,
    'agent_mcp/tools': false,
    'rag': false,
    'models': false,
    'mock_data': false,
    'knowledge_base': false,
    'docs': true,
  });
  const [copiedPath, setCopiedPath] = useState<string | null>(null);

  // Simulation states
  const [simState, setSimState] = useState<'idle' | 'running' | 'pending_payment' | 'processing_payment' | 'paid' | 'confirmed'>('idle');
  const [simLogs, setSimLogs] = useState<{ step: string; status: 'completed' | 'pending' | 'success'; message: string; timestamp: string }[]>([]);
  const [simProgress, setSimProgress] = useState(0);
  const [idempotencyKey, setIdempotencyKey] = useState('idem_sandbox_88cf9b61a320');
  const [stripeForm, setStripeForm] = useState({
    cardNumber: '4242 •••• •••• 4242',
    expiry: '12 / 29',
    cvc: '123',
    cardholder: 'AQUILINO FRANCISCO'
  });

  // MVP Demo states
  const [demoStep, setDemoStep] = useState<number>(0); // 0 means idle/welcome, 1 to 8 are the active steps
  const [guestCountry, setGuestCountry] = useState<'US' | 'MX' | 'BR'>('US');
  const [currency, setCurrency] = useState<'USD' | 'MXN' | 'BRL'>('USD');
  const [isAutoPlaying, setIsAutoPlaying] = useState<boolean>(false);

  // Provider-agnostic enterprise architecture states
  const [llmProvider, setLlmProvider] = useState<string>('Gemini');
  const [llmModel, setLlmModel] = useState<string>('gemini-2.5-flash');
  const [embeddingProvider, setEmbeddingProvider] = useState<string>('Gemini');
  const [vectorStore, setVectorStore] = useState<string>('Memory');
  const [paymentProvider, setPaymentProvider] = useState<string>('Stripe');

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat on message update
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [demoStep]);

  const handleLlmProviderChange = (provider: string) => {
    setLlmProvider(provider);
    if (provider === 'Gemini') setLlmModel('gemini-2.5-flash');
    else if (provider === 'OpenAI') setLlmModel('gpt-4o');
    else if (provider === 'Claude') setLlmModel('claude-3-5-sonnet');
    else if (provider === 'Llama') setLlmModel('llama-3.3-70b');
    else if (provider === 'Ollama') setLlmModel('deepseek-r1:8b');
    else if (provider === 'HuggingFace') setLlmModel('mistral-7b-instruct');
  };

  const handlePaymentProviderChange = (provider: string) => {
    setPaymentProvider(provider);
    if (provider === 'Stripe' || provider === 'PayPal' || provider === 'Adyen' || provider === 'Checkout.com' || provider === 'Klarna') {
      setGuestCountry('US');
      setCurrency('USD');
    } else if (provider === 'Conekta') {
      setGuestCountry('MX');
      setCurrency('MXN');
    } else if (provider === 'Mercado Pago') {
      setGuestCountry('BR');
      setCurrency('BRL');
    }
  };

  const handleGuestCountryChange = (country: 'US' | 'MX' | 'BR') => {
    setGuestCountry(country);
    if (country === 'US') {
      setCurrency('USD');
      setPaymentProvider('Stripe');
    } else if (country === 'MX') {
      setCurrency('MXN');
      setPaymentProvider('Conekta');
    } else if (country === 'BR') {
      setCurrency('BRL');
      setPaymentProvider('Mercado Pago');
    }
  };

  // Dynamic routing parameters, pricing, and steps based on country/currency inputs
  const getStepData = (stepNum: number, country: 'US' | 'MX' | 'BR', curr: 'USD' | 'MXN' | 'BRL') => {
    const rateMap = {
      USD: { symbol: '$', base: 250, label: 'USD' },
      MXN: { symbol: '$', base: 4500, label: 'MXN' },
      BRL: { symbol: 'R$', base: 1200, label: 'BRL' }
    };
    const rate = rateMap[curr] || rateMap.USD;
    const basePrice = rate.base;
    const totalPrice = rate.base * 2;
    const totalFormatted = `${rate.symbol}${totalPrice.toLocaleString(undefined, { minimumFractionDigits: 2 })} ${rate.label}`;
    const baseFormatted = `${rate.symbol}${basePrice.toLocaleString(undefined, { minimumFractionDigits: 2 })} ${rate.label}`;
    const activeProviderName = paymentProvider || (country === 'US' ? 'Stripe' : country === 'MX' ? 'Conekta' : 'Mercado Pago');
    
    const colorsMap: Record<string, string> = {
      'Stripe': '#635bff',
      'PayPal': '#003087',
      'Adyen': '#0abf53',
      'Checkout.com': '#111111',
      'Klarna': '#ffb3c7',
      'Conekta': '#1b255a',
      'Mercado Pago': '#009ee3'
    };
    const activeColor = colorsMap[activeProviderName] || '#635bff';
    
    const webhooksMap: Record<string, string> = {
      'Stripe': 'checkout.session.completed',
      'PayPal': 'checkout.order.approved',
      'Adyen': 'payment.authorised',
      'Checkout.com': 'payment_approved',
      'Klarna': 'order_completed',
      'Conekta': 'order.paid',
      'Mercado Pago': 'payment.created'
    };
    const activeWebhook = webhooksMap[activeProviderName] || 'checkout.session.completed';

    const providerMap = {
      US: { 
        name: `${activeProviderName} Sandbox`, 
        color: activeColor, 
        textColor: `text-[${activeColor}]`, 
        bg: `bg-[${activeColor}]`, 
        webhook: activeWebhook, 
        eventId: `evt_${activeProviderName.toLowerCase().replace(/[^a-z0-9]/g, '')}_test_88cf9b` 
      },
      MX: { 
        name: 'Conekta Sandbox', 
        color: '#1b255a', 
        textColor: 'text-[#1b255a]', 
        bg: 'bg-[#1b255a]', 
        webhook: 'order.paid', 
        eventId: 'evt_conekta_test_88cf9b' 
      },
      BR: { 
        name: 'Mercado Pago Sandbox', 
        color: '#009ee3', 
        textColor: 'text-[#009ee3]', 
        bg: 'bg-[#009ee3]', 
        webhook: 'payment.created', 
        eventId: 'evt_mp_test_88cf9b' 
      }
    };
    const provider = providerMap[country] || providerMap.US;

    const checkoutUrl = country === 'US' 
      ? `https://checkout.stripe.com/pay/cs_test_${idempotencyKey.substring(13)}`
      : country === 'MX'
      ? `https://checkout.conekta.com/pay/order_test_${idempotencyKey.substring(13)}`
      : `https://checkout.mercadopago.com/pay/pref_test_${idempotencyKey.substring(13)}`;

    const steps = [
      {
        id: 1,
        name: "Guest Request",
        title: "1. Guest Request Received",
        langGraphNode: "validate_request",
        crewAiAgent: "ReservationAgent",
        agentStatus: "Parsing request parameters",
        mcpTool: "None",
        ragDoc: "hotel_terms.md",
        lifecycleStatus: "DRAFT" as const,
        log: `[LangGraph:validate_request] Validating parameters. Customer: aquilino.francisco@gmail.com, Room: deluxe-suite, Dates: 2026-07-10 to 2026-07-12 (2 nights).`,
        agentSpeech: `Welcome! Let me check that request for a Deluxe Suite from July 10th to 12th for you.`,
        guestSpeech: `Hi, I'd like to book a Deluxe Suite for 2 nights starting tomorrow, July 10th. Can you help me?`,
      },
      {
        id: 2,
        name: "Availability",
        title: "2. Availability Checked",
        langGraphNode: "check_availability",
        crewAiAgent: "ReservationAgent",
        agentStatus: "Querying room inventory",
        mcpTool: "check_availability",
        ragDoc: "hotel_terms.md",
        lifecycleStatus: "DRAFT" as const,
        log: `[MCP Tool:check_availability] Calling tool with {"room_id": "deluxe-suite", "dates": ["2026-07-10", "2026-07-11"]}. Result: Deluxe Suite is AVAILABLE.`,
        agentSpeech: "Good news! The Deluxe Suite is available for your requested dates. I'm checking the rates next.",
        guestSpeech: "Perfect! Is it available?",
      },
      {
        id: 3,
        name: "Pricing",
        title: "3. Price Calculated",
        langGraphNode: "calculate_price",
        crewAiAgent: "ReservationAgent",
        agentStatus: "Pricing booking details",
        mcpTool: "calculate_price",
        ragDoc: "hotel_terms.md",
        lifecycleStatus: "DRAFT" as const,
        log: `[MCP Tool:calculate_price] Calling tool with {"room_id": "deluxe-suite", "nights": 2}. Result: base_price=${basePrice.toFixed(2)}, total_price=${totalPrice.toFixed(2)}, currency=${curr.toLowerCase()}.`,
        agentSpeech: `The base rate is ${baseFormatted} per night. For 2 nights, the total comes out to ${totalFormatted}.`,
        guestSpeech: "Excellent. How much is the total price?",
      },
      {
        id: 4,
        name: "RAG Retrieval",
        title: "4. Policy Retrieved from RAG",
        langGraphNode: "retrieve_policy",
        crewAiAgent: "ReservationAgent",
        agentStatus: "Confirming policy compliance",
        mcpTool: "None (Vector Store Search)",
        ragDoc: "cancellation_policy.md",
        lifecycleStatus: "DRAFT" as const,
        log: `[RAG Retrieval] Matching embedding vectors against local policy store. Retrieved cancellation_policy.md and payment_policy.md. Semantic similarity score: 0.942.`,
        agentSpeech: `I've retrieved our policies. You can cancel free of charge up to 48 hours prior. Also, our payment policy mandates a secure external checkout session.`,
        guestSpeech: "What are your cancellation policies?",
      },
      {
        id: 5,
        name: "Generate Link",
        title: "5. Payment Link Generated",
        langGraphNode: "generate_payment_link",
        crewAiAgent: "PaymentAgent",
        agentStatus: "Creating Checkout Session",
        mcpTool: "create_payment_link",
        ragDoc: "payment_policy.md",
        lifecycleStatus: "PENDING_PAYMENT" as const,
        log: `[MCP Tool:create_payment_link] Calling tool with {"amount": ${totalPrice.toFixed(2)}, "currency": "${curr.toLowerCase()}", "idempotency_key": "${idempotencyKey}"}. Gateway router selected: ${provider.name}.`,
        agentSpeech: `I've generated a secure checkout payment link for ${totalFormatted} using our ${provider.name} router. Please click the checkout button to complete payment.`,
        guestSpeech: "Great, please send me the payment link.",
      },
      {
        id: 6,
        name: "Pending Payment",
        title: "6. Pending Payment",
        langGraphNode: "awaiting_payment",
        crewAiAgent: "PaymentAgent",
        agentStatus: "Awaiting webhook payment confirmation",
        mcpTool: "check_payment_status",
        ragDoc: "payment_policy.md",
        lifecycleStatus: "PENDING_PAYMENT" as const,
        log: `[LangGraph:awaiting_payment] Polling payment session state. Webhook listener active for ${provider.webhook}.`,
        agentSpeech: `I'm monitoring the ${provider.name} webhook stream for your payment confirmation...`,
        guestSpeech: `[Opening payment checkout link and completing payment...]`,
      },
      {
        id: 7,
        name: "Payment Confirmed",
        title: "7. Payment Confirmed",
        langGraphNode: "confirm_payment",
        crewAiAgent: "PaymentAgent",
        agentStatus: "Verifying webhook signature",
        mcpTool: "confirm_reservation",
        ragDoc: "refund_policy.md",
        lifecycleStatus: "PAID" as const,
        log: `[Webhooks Controller] POST /webhooks/${country.toLowerCase()} received. Signature verified. Event: ${provider.webhook}, Event ID: ${provider.eventId}. State transitioning to PAID.`,
        agentSpeech: "Payment confirmed! Webhook signature is fully verified. We are now locking in your reservation.",
        guestSpeech: "I've completed the payment! Can you check if you received it?",
      },
      {
        id: 8,
        name: "Confirmed",
        title: "8. Reservation Confirmed",
        langGraphNode: "finalize_reservation",
        crewAiAgent: "ReservationAgent",
        agentStatus: "Saving reservation audit report",
        mcpTool: "save_reservation_report",
        ragDoc: "hotel_terms.md",
        lifecycleStatus: "CONFIRMED" as const,
        log: `[MCP Tool:save_reservation_report] Saving reservation audit report JSON to disk. Path: /reports/report_res_001.json. Graph state set to COMPLETED.`,
        agentSpeech: `Your Deluxe Suite is fully booked! I've saved your reservation audit report. Have a wonderful stay starting tomorrow!`,
        guestSpeech: "Awesome! Thank you so much for the quick booking!",
      }
    ];

    return {
      steps,
      rate,
      provider,
      checkoutUrl,
      totalFormatted,
      baseFormatted,
      totalPrice,
      basePrice
    };
  };

  // Helper to extract logs up to current active step
  const getLogsUpToStep = (stepIndex: number, country: 'US' | 'MX' | 'BR', curr: 'USD' | 'MXN' | 'BRL') => {
    const data = getStepData(stepIndex, country, curr);
    const logs: string[] = [];
    for (let i = 0; i < stepIndex; i++) {
      logs.push(data.steps[i].log);
    }
    return logs;
  };

  // Helper to extract messages up to current active step
  const getChatMessages = (stepIndex: number, country: 'US' | 'MX' | 'BR', curr: 'USD' | 'MXN' | 'BRL') => {
    const data = getStepData(stepIndex, country, curr);
    const messages: { sender: 'guest' | 'agent'; text: string; id: number; timestamp: string; llm?: string; ragDoc?: string; mcpTool?: string }[] = [];
    for (let i = 0; i < stepIndex; i++) {
      const step = data.steps[i];
      const minuteOffset = i * 2;
      const formattedTime = `12:${minuteOffset < 10 ? '0' + minuteOffset : minuteOffset} PM`;
      
      if (step.guestSpeech) {
        messages.push({ 
          sender: 'guest', 
          text: step.guestSpeech, 
          id: i * 2, 
          timestamp: formattedTime 
        });
      }
      if (step.agentSpeech) {
        messages.push({ 
          sender: 'agent', 
          text: step.agentSpeech, 
          id: i * 2 + 1, 
          timestamp: formattedTime,
          llm: llmProvider,
          ragDoc: step.ragDoc !== 'None' ? step.ragDoc : undefined,
          mcpTool: step.mcpTool !== 'None' && step.mcpTool !== 'None (Vector Store Search)' ? step.mcpTool : undefined
        });
      }
    }
    return messages;
  };

  // Autoplay hook
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (isAutoPlaying && demoStep > 0 && demoStep < 8 && demoStep !== 6) {
      interval = setInterval(() => {
        setDemoStep(prev => prev + 1);
      }, 2000);
    } else if (demoStep === 6 || demoStep === 8) {
      setIsAutoPlaying(false);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isAutoPlaying, demoStep]);

  // RAG query states
  const [ragQuery, setRagQuery] = useState('');
  const [ragResults, setRagResults] = useState<any[]>([]);
  const [isSearchingRag, setIsSearchingRag] = useState(false);

  // Terminal actions
  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    'Initializing local environment checks...',
    'Python 3.11.8 detected.',
    'Docker container engines verified [v24.0.7]',
    'Git configuration initialized for aquilinoFrancisco',
    'Ready. Explore Phase 1 directories below.'
  ]);

  // Copy code utility
  const handleCopyCode = (text: string, path: string) => {
    navigator.clipboard.writeText(text);
    setCopiedPath(path);
    setTimeout(() => setCopiedPath(null), 2000);
  };

  // Toggle folders
  const toggleFolder = (folderPath: string) => {
    setExpandedFolders(prev => ({ ...prev, [folderPath]: !prev[folderPath] }));
  };

  // Run stream simulator
  const runReservationSimulation = async () => {
    setSimState('running');
    setSimProgress(10);
    setSimLogs([]);
    
    const stepsData = [
      { step: 'validate_request', title: 'State Validation', msg: 'LangGraph node validating email syntax & date constraints' },
      { step: 'check_availability', title: 'Schedule Check', msg: 'MCP tool checking rooms.json & calendars' },
      { step: 'calculate_price', title: 'Pricing Matrix', msg: 'MCP tool checking rate rules: $250.00 x 2 nights = $500.00' },
      { step: 'reservation_agent', title: 'CrewAI: ReservationAgent', msg: 'Reservations manager generating draft records' },
      { step: 'payment_agent', title: 'CrewAI: PaymentAgent', msg: 'Compliance officer invoking MCP create_payment_link' },
    ];

    for (let i = 0; i < stepsData.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 1200));
      const logTime = new Date().toLocaleTimeString();
      setSimLogs(prev => [
        ...prev, 
        { 
          step: stepsData[i].step, 
          status: 'completed', 
          message: stepsData[i].msg, 
          timestamp: logTime 
        }
      ]);
      setSimProgress((i + 1) * 18);
    }

    await new Promise(resolve => setTimeout(resolve, 1000));
    setSimState('pending_payment');
    setSimProgress(90);
    setSimLogs(prev => [
      ...prev,
      {
        step: 'pending_payment',
        status: 'pending',
        message: 'Awaiting webhook transaction authorization link in Stripe Sandbox...',
        timestamp: new Date().toLocaleTimeString()
      }
    ]);
  };

  // Execute mock Stripe Sandbox Payment
  const submitStripePayment = async () => {
    setSimState('processing_payment');
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setSimState('paid');
    setSimLogs(prev => [
      ...prev,
      {
        step: 'webhooks',
        status: 'completed',
        message: 'POST /webhooks/stripe: checkout.session.completed received & signature verified.',
        timestamp: new Date().toLocaleTimeString()
      }
    ]);

    await new Promise(resolve => setTimeout(resolve, 1200));
    setSimState('confirmed');
    setSimProgress(100);
    setSimLogs(prev => [
      ...prev,
      {
        step: 'confirmed',
        status: 'success',
        message: 'Reservation state set to CONFIRMED. Audit JSON report saved to /reports/report_res_001.json!',
        timestamp: new Date().toLocaleTimeString()
      }
    ]);
  };

  // Reset simulation
  const resetSimulation = () => {
    setSimState('idle');
    setSimLogs([]);
    setSimProgress(0);
    // Generate new idempotency key on restart
    setIdempotencyKey('idem_sandbox_' + Math.random().toString(36).substring(2, 14));
  };

  // Run semantic RAG Search
  const executeRagSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ragQuery.trim()) return;

    setIsSearchingRag(true);
    setTimeout(() => {
      const normalizedQuery = ragQuery.toLowerCase();
      const hits = MOCK_RAG_DATABASE.filter(doc => {
        return doc.title.toLowerCase().includes(normalizedQuery) ||
               doc.content.toLowerCase().includes(normalizedQuery) ||
               doc.tags.some(tag => tag.includes(normalizedQuery));
      });
      setRagResults(hits);
      setIsSearchingRag(false);
    }, 800);
  };

  // File explorer tree component
  const renderTree = (nodes: FolderNode[]) => {
    return (
      <div className="pl-3 border-l border-slate-800 select-none">
        {nodes.map(node => {
          const isFolder = node.type === 'folder';
          const isExpanded = expandedFolders[node.path] || false;
          const isFileSelected = selectedFile?.path === node.path;

          return (
            <div key={node.path} className="my-1">
              <div 
                onClick={() => {
                  if (isFolder) {
                    toggleFolder(node.path);
                  } else {
                    const foundFile = REPO_FILES[node.path];
                    if (foundFile) setSelectedFile(foundFile);
                  }
                }}
                className={`flex items-center gap-2 py-1 px-2 rounded-md cursor-pointer transition-colors ${
                  isFileSelected 
                    ? 'bg-emerald-950/40 text-emerald-300 border border-emerald-900/40' 
                    : 'text-slate-300 hover:bg-slate-800/40'
                }`}
              >
                {isFolder ? (
                  <>
                    {isExpanded ? <ChevronDown size={14} className="text-slate-400" /> : <ChevronRight size={14} className="text-slate-400" />}
                    {isExpanded ? <FolderOpen size={16} className="text-emerald-400" /> : <Folder size={16} className="text-emerald-500" />}
                    <span className="font-sans font-medium text-xs text-slate-200">{node.name}</span>
                  </>
                ) : (
                  <>
                    <span className="w-3.5 h-3.5 flex items-center justify-center">
                      <File size={14} className={isFileSelected ? 'text-emerald-400' : 'text-slate-400'} />
                    </span>
                    <span className={`font-mono text-xs ${isFileSelected ? 'text-emerald-300 font-semibold' : 'text-slate-300'}`}>
                      {node.name}
                    </span>
                    {node.name.endsWith('.md') && (
                      <span className="text-[9px] px-1 py-0.5 rounded bg-slate-800 text-slate-400 font-sans">Doc</span>
                    )}
                    {node.name.endsWith('.json') && (
                      <span className="text-[9px] px-1 py-0.5 rounded bg-amber-950/40 text-amber-300 font-sans">JSON</span>
                    )}
                  </>
                )}
              </div>
              
              {isFolder && isExpanded && node.children && (
                <div className="mt-0.5">
                  {renderTree(node.children)}
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-200 font-sans selection:bg-emerald-800/40 flex flex-col">
      
      {/* HEADER BAR */}
      <header className="border-b border-slate-800/80 bg-[#090e18] px-6 py-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1 rounded bg-emerald-500/10 border border-emerald-500/20">
              <Sparkles className="text-emerald-400" size={18} />
            </span>
            <h1 className="text-lg font-bold text-slate-100 tracking-tight">
              Hospitality Reservation Payment Agent
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Provider-agnostic agentic booking workflows with LangGraph, CrewAI, and Model Context Protocol.
          </p>
        </div>

        {/* Action badges and project links */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs bg-emerald-950/60 border border-emerald-900/50 text-emerald-400 px-2.5 py-1 rounded-full font-medium flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Provider-Agnostic
          </span>
          <span className="text-xs bg-slate-800/60 border border-slate-700/50 text-slate-300 px-2.5 py-1 rounded-full font-medium flex items-center gap-1">
            Multi-Provider
          </span>
          <span className="text-xs bg-slate-800/60 border border-slate-700/50 text-slate-300 px-2.5 py-1 rounded-full font-medium flex items-center gap-1">
            Enterprise Architecture
          </span>
          <a 
            href="https://github.com/aquilinoFrancisco/hospitality-reservation-payment-agent" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-xs bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-emerald-400 px-3 py-1 rounded-lg font-medium transition-all flex items-center gap-1.5"
          >
            <Github size={14} />
            GitHub Repo
            <ExternalLink size={10} />
          </a>
        </div>
      </header>

      {/* CORE NAVIGATION TABS */}
      <nav className="flex border-b border-slate-800/60 bg-[#080c14] px-6">
        <button 
          onClick={() => setActiveTab('explorer')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition-all cursor-pointer ${
            activeTab === 'explorer' 
              ? 'border-emerald-500 text-emerald-400 bg-emerald-950/10' 
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FolderOpen size={14} />
          Repository Explorer
        </button>
        <button 
          onClick={() => setActiveTab('simulator')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition-all cursor-pointer ${
            activeTab === 'simulator' 
              ? 'border-emerald-500 text-emerald-400 bg-emerald-950/10' 
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Cpu size={14} />
          Agent Payment Simulator
          <span className="text-[9px] px-1 py-0.2 bg-emerald-500/10 border border-emerald-500/20 rounded text-emerald-400">Live</span>
        </button>
        <button 
          onClick={() => setActiveTab('providers')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition-all cursor-pointer ${
            activeTab === 'providers' 
              ? 'border-emerald-500 text-emerald-400 bg-emerald-950/10' 
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Sliders size={14} />
          AI Providers
          <span className="text-[9px] px-1 py-0.2 bg-sky-500/10 border border-sky-500/20 rounded text-sky-400">Config</span>
        </button>
        <button 
          onClick={() => setActiveTab('rag')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition-all cursor-pointer ${
            activeTab === 'rag' 
              ? 'border-emerald-500 text-emerald-400 bg-emerald-950/10' 
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Database size={14} />
          Local RAG Search
        </button>
        <button 
          onClick={() => setActiveTab('docs')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition-all cursor-pointer ${
            activeTab === 'docs' 
              ? 'border-emerald-500 text-emerald-400 bg-emerald-950/10' 
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <ShieldCheck size={14} />
          Security & Architecture
        </button>
      </nav>

      {/* WORKSPACE AREA */}
      <main className="flex-1 flex flex-col lg:flex-row overflow-hidden bg-[#05080e]">
        
        {/* VIEW 1: REPOSITORY EXPLORER */}
        {activeTab === 'explorer' && (
          <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
            
            {/* FILE EXPLORER SIDEBAR */}
            <section className="w-full lg:w-80 border-r border-slate-900/60 bg-[#080d16] p-4 flex flex-col overflow-y-auto">
              <div className="flex items-center justify-between text-xs text-slate-400 font-semibold uppercase tracking-wider mb-3 px-1">
                <span>Repository Files</span>
                <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-mono">
                  Phase 1
                </span>
              </div>
              
              <div className="flex-1 overflow-y-auto pr-1">
                {renderTree(REPO_TREE)}
              </div>

              {/* GIT STATUS PANEL SUMMARY */}
              <div className="mt-4 pt-4 border-t border-slate-800/80">
                <div className="flex items-center gap-1.5 text-xs text-slate-300 font-semibold mb-2">
                  <GitBranch size={13} className="text-sky-400" />
                  <span>git status</span>
                </div>
                <div className="font-mono text-[10px] text-slate-400 leading-relaxed bg-[#060a10] p-2.5 rounded-lg border border-slate-900">
                  <div>On branch <span className="text-emerald-400">main</span></div>
                  <div>nothing to commit, working tree clean</div>
                  <div className="text-slate-500 text-[9px] mt-1.5">
                    Prepared for upload:
                    <div className="text-sky-400 mt-0.5 truncate">https://github.com/aquilinoFrancisco/...</div>
                  </div>
                </div>
              </div>
            </section>

            {/* CODE WORKSPACE EDITOR */}
            <section className="flex-1 flex flex-col bg-[#05080e] overflow-hidden min-h-[400px]">
              {selectedFile ? (
                <div className="flex-1 flex flex-col overflow-hidden">
                  
                  {/* EDITOR CONTROLS */}
                  <div className="bg-[#080d16] border-b border-slate-900/80 px-4 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="p-1 rounded bg-slate-800/50">
                        <File size={13} className="text-emerald-400" />
                      </span>
                      <span className="font-mono text-xs text-slate-300 font-semibold truncate">
                        hospitality-reservation-payment-agent/{selectedFile.path}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleCopyCode(selectedFile.content, selectedFile.path)}
                        className="text-slate-400 hover:text-emerald-400 p-1.5 hover:bg-slate-800/50 rounded-lg transition-all cursor-pointer"
                        title="Copy code to clipboard"
                      >
                        {copiedPath === selectedFile.path ? (
                          <span className="text-xs text-emerald-400 font-sans flex items-center gap-1">
                            <Check size={12} /> Copied!
                          </span>
                        ) : (
                          <Copy size={14} />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* FILE INFO BOX */}
                  <div className="bg-slate-950/40 px-5 py-3 border-b border-slate-900/30 flex items-start gap-2.5">
                    <AlertCircle size={14} className="text-emerald-500 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-slate-400 leading-normal">
                      <strong className="text-slate-200">Module Blueprint:</strong> {selectedFile.description}
                    </p>
                  </div>

                  {/* CODE PANEL */}
                  <div className="flex-1 overflow-auto bg-[#05080e] p-6 font-mono text-xs leading-relaxed text-slate-300">
                    <pre className="relative select-text">
                       <code 
                        dangerouslySetInnerHTML={{ 
                          __html: highlightCode(selectedFile.content, selectedFile.language) 
                        }} 
                      />
                    </pre>
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-slate-500 p-6 bg-[#05080e]">
                  <File size={40} className="text-slate-700 mb-2" />
                  <p className="text-sm font-sans">Select a file from the repository tree to inspect its placeholder code.</p>
                </div>
              )}
            </section>
          </div>
        )}

        {/* VIEW 2: STREAM AGENT SIMULATOR */}
        {activeTab === 'simulator' && (() => {
          const currentData = getStepData(demoStep, guestCountry, currency);
          const currentStep = demoStep > 0 ? currentData.steps[demoStep - 1] : null;
          const isAtPaymentStep = demoStep === 6;
          const isDemoFinished = demoStep === 8;

          return (
            <div className="flex-1 flex flex-col xl:flex-row overflow-y-auto p-6 gap-6">
              
              {/* LEFT DASHBOARD COLUMN */}
              <div className="flex-1 flex flex-col gap-6">
                
                {/* CONFIG & INITIATE BLOCK */}
                <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5 shadow-lg">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Terminal size={16} className="text-emerald-400" />
                      <h2 className="text-sm font-bold text-slate-200">Simulation Configuration</h2>
                    </div>
                    <span className="text-[10px] font-mono bg-emerald-950/40 text-emerald-400 border border-emerald-900/50 px-2 py-0.5 rounded">
                      Gateway Router Live
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
                    <div>
                      <label className="block text-[10px] text-slate-400 uppercase tracking-wider font-semibold mb-1">
                        Guest Country Profile
                      </label>
                      <select 
                        disabled={demoStep > 0}
                        value={guestCountry}
                        onChange={(e) => {
                          const val = e.target.value as 'US' | 'MX' | 'BR';
                          setGuestCountry(val);
                          if (val === 'US') setCurrency('USD');
                          else if (val === 'MX') setCurrency('MXN');
                          else if (val === 'BR') setCurrency('BRL');
                        }}
                        className="w-full bg-[#05080e] border border-slate-800 rounded-lg p-2 text-xs font-sans text-slate-300 focus:border-emerald-500 outline-none cursor-pointer"
                      >
                        <option value="US">United States (Stripe)</option>
                        <option value="MX">Mexico (Conekta)</option>
                        <option value="BR">Brazil (Mercado Pago)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[10px] text-slate-400 uppercase tracking-wider font-semibold mb-1">
                        Active Currency
                      </label>
                      <select 
                        disabled={demoStep > 0}
                        value={currency}
                        onChange={(e) => setCurrency(e.target.value as 'USD' | 'MXN' | 'BRL')}
                        className="w-full bg-[#05080e] border border-slate-800 rounded-lg p-2 text-xs font-sans text-slate-300 focus:border-emerald-500 outline-none cursor-pointer"
                      >
                        <option value="USD">USD ($)</option>
                        <option value="MXN">MXN ($)</option>
                        <option value="BRL">BRL (R$)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[10px] text-slate-400 uppercase tracking-wider font-semibold mb-1">
                        Room Selection
                      </label>
                      <select disabled className="w-full bg-[#05080e] border border-slate-800 rounded-lg p-2 text-xs font-sans text-slate-300 cursor-not-allowed">
                        <option>Deluxe Suite ({currentData.baseFormatted} / night)</option>
                      </select>
                    </div>
                  </div>

                  {/* CONTROLS ROW */}
                  <div className="flex flex-wrap items-center justify-between border-t border-slate-800/60 pt-4 gap-4">
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] text-slate-400">Idempotency Key:</span>
                      <span className="font-mono text-xs text-emerald-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-900">{idempotencyKey}</span>
                    </div>

                    <div className="flex items-center gap-2.5">
                      {demoStep === 0 ? (
                        <button
                          onClick={() => setDemoStep(1)}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs py-2 px-4 rounded-lg cursor-pointer transition-all flex items-center gap-1.5 shadow-lg shadow-emerald-950/20"
                        >
                          <Play size={13} />
                          Start MVP Demo
                        </button>
                      ) : (
                        <>
                          <button
                            disabled={isAtPaymentStep || isDemoFinished}
                            onClick={() => setDemoStep(prev => prev + 1)}
                            className={`font-semibold text-xs py-2 px-4 rounded-lg cursor-pointer transition-all flex items-center gap-1.5 ${
                              isAtPaymentStep || isDemoFinished
                                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                                : 'bg-emerald-600 hover:bg-emerald-500 text-white'
                            }`}
                          >
                            <ChevronRight size={13} />
                            {isAtPaymentStep ? "Awaiting Payment" : isDemoFinished ? "Booking Confirmed" : "Next Step"}
                          </button>

                          <button
                            onClick={() => setIsAutoPlaying(!isAutoPlaying)}
                            disabled={isAtPaymentStep || isDemoFinished}
                            className={`font-semibold text-xs py-2 px-4 rounded-lg cursor-pointer transition-all flex items-center gap-1.5 ${
                              isAtPaymentStep || isDemoFinished
                                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                                : isAutoPlaying
                                ? 'bg-amber-600 hover:bg-amber-500 text-white animate-pulse'
                                : 'bg-slate-700 hover:bg-slate-600 text-slate-200'
                            }`}
                          >
                            {isAutoPlaying ? "Pause Auto Run" : "Auto Run Demo"}
                          </button>
                        </>
                      )}

                      <button
                        onClick={() => {
                          setDemoStep(0);
                          setIsAutoPlaying(false);
                          setIdempotencyKey('idem_sandbox_' + Math.random().toString(36).substring(2, 14));
                        }}
                        className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs py-2 px-4 rounded-lg cursor-pointer transition-all flex items-center gap-1.5"
                      >
                        <RefreshCw size={13} />
                        Reset
                      </button>
                    </div>
                  </div>
                </div>

                {/* GRAPH WORKFLOW CARD */}
                <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5 shadow-md">
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-2">
                    <Cpu size={14} className="text-emerald-400" />
                    LangGraph Workflow Orchestration (8 Nodes)
                  </h3>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {getStepData(8, guestCountry, currency).steps.map((step, idx) => {
                      const isCompleted = demoStep > idx + 1;
                      const isActive = demoStep === idx + 1;
                      const isFuture = demoStep < idx + 1;

                      return (
                        <div 
                          key={step.id} 
                          className={`p-3 rounded-lg border transition-all flex flex-col justify-between min-h-[75px] relative overflow-hidden ${
                            isActive 
                              ? 'border-emerald-500 bg-emerald-950/20 shadow-lg shadow-emerald-950/40 ring-1 ring-emerald-500/30' 
                              : isCompleted 
                              ? 'border-emerald-900/60 bg-[#05080e]/60 opacity-80' 
                              : 'border-slate-800/80 bg-[#05080e]/20 opacity-50'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className={`text-[10px] font-mono uppercase tracking-wider font-semibold ${
                              isActive ? 'text-emerald-400' : isCompleted ? 'text-emerald-500/80' : 'text-slate-500'
                            }`}>
                              Node {idx + 1}
                            </span>
                            {isCompleted && <CheckCircle2 size={12} className="text-emerald-400" />}
                            {isActive && (
                              <span className="flex h-2 w-2 relative">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                              </span>
                            )}
                          </div>
                          
                          <div className="mt-1.5">
                            <div className="font-sans font-bold text-xs text-slate-200 truncate">{step.name}</div>
                            <div className="font-mono text-[9px] text-slate-500 mt-0.5 truncate">{step.langGraphNode}</div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* VISUAL DIALOG STREAM CONTAINER */}
                <div className="flex-1 min-h-[400px] border border-slate-800/80 bg-[#080d16] rounded-xl flex flex-col overflow-hidden shadow-md">
                  
                  {/* CONVERSATION BAR */}
                  <div className="px-4 py-3 bg-slate-950/40 border-b border-slate-900/60 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <MessageSquare size={14} className="text-emerald-400" />
                      <span className="text-xs font-bold text-slate-300">Live Agent Webhook & Orchestration Stream</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-slate-400 font-mono">Status:</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-semibold ${
                        demoStep === 0 
                          ? 'bg-slate-900 text-slate-400' 
                          : isDemoFinished 
                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-900/40' 
                          : 'bg-amber-950/40 text-amber-400 border border-amber-900/40 animate-pulse'
                      }`}>
                        {demoStep === 0 ? 'IDLE' : isDemoFinished ? 'COMPLETED' : 'EXECUTING'}
                      </span>
                    </div>
                  </div>

                  {/* ACTIVE NODES SUMMARY BAR */}
                  {demoStep > 0 && currentStep && (
                    <div className="bg-[#0c1322] border-b border-slate-800/40 px-5 py-3 grid grid-cols-1 sm:grid-cols-4 gap-3.5 text-xs text-slate-300">
                      <div className="flex flex-col">
                        <span className="text-[9px] text-slate-500 font-mono uppercase">CrewAI Agent</span>
                        <span className="font-semibold text-slate-200 flex items-center gap-1.5 mt-0.5">
                          <Bot size={13} className="text-emerald-400" />
                          {currentStep.crewAiAgent}
                        </span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-[9px] text-slate-500 font-mono uppercase">Agent State</span>
                        <span className="font-semibold text-slate-300 mt-0.5 truncate">{currentStep.agentStatus}</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-[9px] text-slate-500 font-mono uppercase">MCP Bound Tool</span>
                        <span className="font-mono text-[11px] text-amber-300 font-medium mt-0.5 truncate">{currentStep.mcpTool}</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-[9px] text-slate-500 font-mono uppercase">Active Lifecycle Status</span>
                        <span className="font-bold text-[10px] text-emerald-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-900/60 mt-0.5 text-center self-start font-mono">
                          {currentStep.lifecycleStatus}
                        </span>
                      </div>
                    </div>
                  )}

                  {/* STREAM BUBBLES SCROLL */}
                  <div className="flex-1 p-5 overflow-y-auto space-y-4 max-h-[300px]">
                    <AnimatePresence>
                      {demoStep === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-500">
                          <Sparkles size={32} className="text-emerald-500/80 mb-2 animate-bounce" />
                          <h4 className="text-xs font-bold text-slate-300 mb-1">Agent Orchestration Workspace Sandbox</h4>
                          <p className="text-[11px] max-w-sm mx-auto leading-relaxed text-slate-400">
                            Configure the guest country and currency parameters above, then click <strong>"Start MVP Demo"</strong> to visualize the step-by-step routing flow.
                          </p>
                        </div>
                      ) : (
                        <>
                          {getChatMessages(demoStep, guestCountry, currency).map((msg) => {
                            const isAgent = msg.sender === 'agent';
                            return (
                              <motion.div 
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                key={msg.id}
                                className={`flex gap-3 max-w-[85%] ${isAgent ? 'mr-auto' : 'ml-auto flex-row-reverse'}`}
                              >
                                <div className={`w-7 h-7 rounded-lg flex items-center justify-center border flex-shrink-0 ${
                                  isAgent 
                                    ? 'bg-emerald-950/50 border-emerald-900/50 text-emerald-400' 
                                    : 'bg-slate-850/60 border-slate-800 text-slate-300'
                                }`}>
                                  {isAgent ? <Bot size={14} /> : <User size={14} />}
                                </div>
                                
                                <div className="space-y-1">
                                  <div className={`p-3 rounded-xl text-xs leading-relaxed ${
                                    isAgent 
                                      ? 'bg-slate-900 border border-slate-850 text-slate-200 rounded-tl-none' 
                                      : 'bg-emerald-900/20 border border-emerald-900/30 text-emerald-200 rounded-tr-none'
                                  }`}>
                                    {msg.text}

                                    {/* MOCK SANDBOX PAYMENT EMBEDDED CARD ONLY IN STEP 6 */}
                                    {msg.text.includes('[Opening payment checkout link') && (
                                      <div className="mt-3 bg-slate-950 border border-slate-800 rounded-lg p-3.5 text-slate-300 space-y-3 font-sans shadow-lg max-w-sm">
                                        <div className="flex items-center justify-between border-b border-slate-900 pb-2">
                                          <div className="flex items-center gap-2">
                                            <CreditCard size={14} className="text-emerald-400" />
                                            <span className="text-xs font-bold font-mono">{currentData.provider.name}</span>
                                          </div>
                                          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold font-mono">Secure Link Checkout</span>
                                        </div>

                                        <div className="space-y-2">
                                          <div className="flex justify-between text-xs">
                                            <span className="text-slate-500">Amount due:</span>
                                            <span className="font-bold text-slate-200 font-mono">{currentData.totalFormatted}</span>
                                          </div>
                                          <div className="flex justify-between text-xs">
                                            <span className="text-slate-500">Idempotency:</span>
                                            <span className="font-mono text-slate-400 text-[10px] truncate max-w-[150px]">{idempotencyKey}</span>
                                          </div>
                                        </div>

                                        <div className="bg-[#05080e] p-2.5 rounded border border-slate-900 font-mono text-[10px] text-slate-500 space-y-1">
                                          <div>Card: 4242 •••• •••• 4242</div>
                                          <div>Cardholder: AQUILINO FRANCISCO</div>
                                        </div>

                                        <button
                                          type="button"
                                          onClick={async () => {
                                            // Directly transition from step 6 (pending checkout) to step 7 (paid webhook)
                                            setDemoStep(7);
                                          }}
                                          className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[11px] py-2 rounded transition-all cursor-pointer shadow-md shadow-emerald-950/20 uppercase tracking-wider font-mono flex items-center justify-center gap-1.5"
                                        >
                                          <ShieldCheck size={12} />
                                          Simulate External Secure Pay
                                        </button>
                                      </div>
                                    )}
                                  </div>

                                  {/* META INJECTED DETAILS UNDER AGENT BUBBLES */}
                                  {isAgent && (msg.ragDoc || msg.mcpTool) && (
                                    <div className="flex flex-wrap gap-1.5 pt-0.5">
                                      {msg.ragDoc && (
                                        <span className="text-[9px] font-mono bg-purple-950/40 text-purple-400 border border-purple-900/40 px-1.5 py-0.2 rounded flex items-center gap-1">
                                          <Database size={9} /> RAG Grounded: {msg.ragDoc}
                                        </span>
                                      )}
                                      {msg.mcpTool && (
                                        <span className="text-[9px] font-mono bg-amber-950/40 text-amber-300 border border-amber-900/40 px-1.5 py-0.2 rounded flex items-center gap-1">
                                          <Terminal size={9} /> MCP Tool: {msg.mcpTool}
                                        </span>
                                      )}
                                      {msg.llm && (
                                        <span className="text-[9px] font-mono bg-blue-950/30 text-blue-400 border border-blue-900/30 px-1.5 py-0.2 rounded flex items-center gap-1">
                                          <Cpu size={9} /> LLM: {msg.llm} ({llmModel})
                                        </span>
                                      )}
                                    </div>
                                  )}
                                  
                                  <div className="text-[9px] text-slate-500 font-mono text-right">{msg.timestamp}</div>
                                </div>
                              </motion.div>
                            );
                          })}
                        </>
                      )}
                    </AnimatePresence>
                    <div ref={chatEndRef} />
                  </div>
                </div>

              </div>

              {/* RIGHT TERMINAL CONTEXT COLUMN */}
              <div className="w-full xl:w-96 flex flex-col gap-6">
                
                {/* INTERACTIVE WORKFLOW STATE CHART */}
                <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5 shadow-md flex flex-col justify-between min-h-[220px]">
                  <div>
                    <div className="flex items-center justify-between mb-3.5">
                      <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                        <Layers size={14} className="text-sky-400" />
                        Active State Engine context
                      </h3>
                      <span className="text-[10px] bg-sky-950/40 text-sky-400 border border-sky-900/40 px-1.5 py-0.5 rounded font-mono">
                        Memory Context
                      </span>
                    </div>

                    <div className="space-y-3 font-mono text-xs">
                      <div className="flex justify-between items-center border-b border-slate-900 pb-1.5">
                        <span className="text-slate-500">Guest Profile Email:</span>
                        <span className="text-slate-300">aquilino.francisco@gmail.com</span>
                      </div>
                      <div className="flex justify-between items-center border-b border-slate-900 pb-1.5">
                        <span className="text-slate-500">Reserved Room ID:</span>
                        <span className="text-slate-300">deluxe-suite</span>
                      </div>
                      <div className="flex justify-between items-center border-b border-slate-900 pb-1.5">
                        <span className="text-slate-500">Active Currency Ingress:</span>
                        <span className="text-emerald-400 font-bold">{currency}</span>
                      </div>
                      <div className="flex justify-between items-center border-b border-slate-900 pb-1.5">
                        <span className="text-slate-500">Gateway Provider Router:</span>
                        <span className="text-indigo-400 font-bold">{currentData.provider.name}</span>
                      </div>
                      <div className="flex justify-between items-center border-b border-slate-900 pb-1.5">
                        <span className="text-slate-500">Amount Parameter:</span>
                        <span className="text-slate-300 font-bold">{currentData.totalFormatted}</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-900 text-[10px] text-slate-500 mt-4 leading-normal flex items-start gap-1.5">
                    <ShieldCheck size={14} className="text-sky-400 mt-0.5 flex-shrink-0" />
                    <span>Double spending and parallel draft collision is blocked using unique idempotency checks bound to each payment gateway transaction session.</span>
                  </div>
                </div>

                {/* ORCHESTRATION EVENT TERMINAL */}
                <div className="bg-[#05080e] border border-slate-800/85 rounded-xl flex-1 min-h-[300px] flex flex-col overflow-hidden shadow-lg">
                  <div className="bg-[#080d16] border-b border-slate-900/80 px-4 py-2.5 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs text-slate-300 font-bold">
                      <Terminal size={13} className="text-emerald-400" />
                      <span>Agent Event Logger Terminal</span>
                    </div>
                    <span className="text-[9px] font-mono text-slate-500">stdout</span>
                  </div>

                  {/* LOGGER WINDOW */}
                  <div className="flex-1 p-4 font-mono text-[10.5px] leading-relaxed text-slate-400 overflow-y-auto space-y-2">
                    {demoStep === 0 ? (
                      <div className="text-slate-600 italic">No events logged. Start the MVP demo to observe node transition telemetry.</div>
                    ) : (
                      getLogsUpToStep(demoStep, guestCountry, currency).map((logLine, index) => (
                        <div key={index} className="border-l-2 border-emerald-950 pl-2 text-slate-300">
                          <span className="text-slate-500 text-[9px] select-none">[{new Date().toLocaleDateString()} 12:{index*2 < 10 ? '0'+index*2 : index*2}:00]</span> {logLine}
                        </div>
                      ))
                    )}
                  </div>
                </div>

              </div>

            </div>
          );
        })()}

        {/* VIEW 2.5: AI PROVIDERS CONFIGURATION PANEL */}
        {activeTab === 'providers' && (
          <div className="flex-1 flex flex-col p-6 overflow-y-auto">
            {/* PROVIDERS HEADER */}
            <div className="mb-6">
              <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                <Sliders size={16} className="text-emerald-400" />
                AI Providers & Infrastructure Engine
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Configure models, vector stores, and gateway endpoints. Changes immediately update the orchestration context of the live booking workflow.
              </p>
            </div>

            {/* BENTO GRID OF CONFIGURATION PANELS */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* LLM PROVIDER */}
              <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5 shadow-md flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      <Cpu size={14} className="text-purple-400" />
                      LLM Provider Routing
                    </h3>
                    <span className="text-[10px] bg-purple-950/40 text-purple-400 border border-purple-900/40 px-2 py-0.5 rounded font-mono font-semibold">
                      Agent Orchestrator
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-400 mb-4 font-sans leading-normal">
                    Manages the main LLM behind CrewAI and LangGraph workflows. Controls natural language parsing and task decomposition.
                  </p>

                  <div className="space-y-3.5 mb-4">
                    <div>
                      <label className="text-[10px] text-slate-500 font-mono uppercase block mb-1">Select Provider</label>
                      <select 
                        value={llmProvider}
                        onChange={(e) => handleLlmProviderChange(e.target.value)}
                        className="w-full bg-[#05080e] border border-slate-800 hover:border-slate-700 text-xs text-slate-200 rounded-lg p-2 outline-none cursor-pointer font-sans"
                      >
                        <option value="Gemini">Gemini (Google DeepMind)</option>
                        <option value="OpenAI">OpenAI</option>
                        <option value="Claude">Claude (Anthropic)</option>
                        <option value="Llama">Llama 3 (Meta)</option>
                        <option value="Ollama">Ollama (Local Deployment)</option>
                        <option value="HuggingFace">HuggingFace Serverless</option>
                      </select>
                    </div>

                    <div className="grid grid-cols-2 gap-3 bg-slate-950/50 p-3 rounded-lg border border-slate-900">
                      <div>
                        <span className="text-[9px] text-slate-500 font-mono uppercase block">Active Model</span>
                        <span className="text-xs text-slate-200 font-bold font-mono mt-0.5 block truncate">{llmModel}</span>
                      </div>
                      <div>
                        <span className="text-[9px] text-slate-500 font-mono uppercase block">API Connection</span>
                        <span className="text-xs text-emerald-400 font-bold mt-0.5 block flex items-center gap-1">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                          Mocked OK
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="text-[10px] text-slate-500 border-t border-slate-900 pt-3 flex justify-between items-center">
                  <span>Routing latency: <span className="text-slate-300 font-mono">140ms</span></span>
                  <span className="font-mono text-purple-400">api.routing.enterprise</span>
                </div>
              </div>

              {/* EMBEDDING PROVIDER */}
              <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5 shadow-md flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      <Fingerprint size={14} className="text-blue-400" />
                      Embedding Provider
                    </h3>
                    <span className="text-[10px] bg-blue-950/40 text-blue-400 border border-blue-900/40 px-2 py-0.5 rounded font-mono font-semibold">
                      Vector Indexer
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-400 mb-4 font-sans leading-normal">
                    Generates numerical vectors for semantic search in RAG files. Governs RAG indexing accuracy.
                  </p>

                  <div className="space-y-3.5 mb-4">
                    <div>
                      <label className="text-[10px] text-slate-500 font-mono uppercase block mb-1">Select Embedding Provider</label>
                      <select 
                        value={embeddingProvider}
                        onChange={(e) => setEmbeddingProvider(e.target.value)}
                        className="w-full bg-[#05080e] border border-slate-800 hover:border-slate-700 text-xs text-slate-200 rounded-lg p-2 outline-none cursor-pointer font-sans"
                      >
                        <option value="Gemini">Gemini embeddings (text-embedding-004)</option>
                        <option value="OpenAI">OpenAI embeddings (text-embedding-3-small)</option>
                        <option value="HuggingFace">HuggingFace (bge-large-en-v1.5)</option>
                        <option value="Voyage AI">Voyage AI (voyage-3)</option>
                        <option value="Ollama">Ollama local embeddings</option>
                        <option value="Mock">Mock Deterministic Embedder</option>
                      </select>
                    </div>

                    <div className="grid grid-cols-2 gap-3 bg-slate-950/50 p-3 rounded-lg border border-slate-900">
                      <div>
                        <span className="text-[9px] text-slate-500 font-mono uppercase block">Dimensionality</span>
                        <span className="text-xs text-slate-200 font-bold font-mono mt-0.5 block">
                          {embeddingProvider === 'OpenAI' ? '1536 dimensions' : embeddingProvider === 'Voyage AI' ? '1024 dimensions' : '768 dimensions'}
                        </span>
                      </div>
                      <div>
                        <span className="text-[9px] text-slate-500 font-mono uppercase block">Index Status</span>
                        <span className="text-xs text-emerald-400 font-bold mt-0.5 block flex items-center gap-1">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                          SYNCHRONIZED
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="text-[10px] text-slate-500 border-t border-slate-900 pt-3 flex justify-between items-center">
                  <span>Batch size capability: <span className="text-slate-300 font-mono">2048</span></span>
                  <span className="font-mono text-blue-400">embeddings.engine</span>
                </div>
              </div>

              {/* VECTOR STORE */}
              <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5 shadow-md flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      <Database size={14} className="text-pink-400" />
                      Vector Store Database
                    </h3>
                    <span className="text-[10px] bg-pink-950/40 text-pink-400 border border-pink-900/40 px-2 py-0.5 rounded font-mono font-semibold">
                      Semantic Memory
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-400 mb-4 font-sans leading-normal">
                    Stores vector chunks of policy files. Resolves matching scores dynamically during user query lookup.
                  </p>

                  <div className="space-y-3.5 mb-4">
                    <div>
                      <label className="text-[10px] text-slate-500 font-mono uppercase block mb-1">Select Vector Store</label>
                      <select 
                        value={vectorStore}
                        onChange={(e) => setVectorStore(e.target.value)}
                        className="w-full bg-[#05080e] border border-slate-800 hover:border-slate-700 text-xs text-slate-200 rounded-lg p-2 outline-none cursor-pointer font-sans"
                      >
                        <option value="Memory">Local Memory Array (No External Server)</option>
                        <option value="FAISS">FAISS (Facebook AI Similarity Search)</option>
                        <option value="PGVector">PGVector (PostgreSQL relational Vector Extension)</option>
                        <option value="OpenSearch">OpenSearch Service Instance</option>
                        <option value="Pinecone">Pinecone Cloud Vector Database</option>
                      </select>
                    </div>

                    <div className="grid grid-cols-2 gap-3 bg-slate-950/50 p-3 rounded-lg border border-slate-900">
                      <div>
                        <span className="text-[9px] text-slate-500 font-mono uppercase block">Connection Status</span>
                        <span className="text-xs text-slate-200 font-bold font-mono mt-0.5 block truncate">
                          {vectorStore === 'Pinecone' ? 'pinecone://us-east1' : vectorStore === 'PGVector' ? 'postgresql://localhost' : 'localhost:in_memory'}
                        </span>
                      </div>
                      <div>
                        <span className="text-[9px] text-slate-500 font-mono uppercase block">Metrics Index</span>
                        <span className="text-xs text-pink-400 font-bold mt-0.5 block">
                          Cosine Similarity
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="text-[10px] text-slate-500 border-t border-slate-900 pt-3 flex justify-between items-center">
                  <span>Document chunk size: <span className="text-slate-300 font-mono">512 tokens</span></span>
                  <span className="font-mono text-pink-400">vector.db.connection</span>
                </div>
              </div>

              {/* PAYMENT GATEWAY ROUTER */}
              <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5 shadow-md flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      <CreditCard size={14} className="text-emerald-400" />
                      Payment Provider Gateway
                    </h3>
                    <span className="text-[10px] bg-emerald-950/40 text-emerald-400 border border-emerald-900/40 px-2 py-0.5 rounded font-mono font-semibold">
                      Enterprise Router
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-400 mb-4 font-sans leading-normal">
                    Provider-agnostic payment gateway router. Chooses Stripe, PayPal, or local processors according to region rules.
                  </p>

                  <div className="space-y-3.5 mb-4">
                    <div>
                      <label className="text-[10px] text-slate-500 font-mono uppercase block mb-1">Select Gateway Provider</label>
                      <select 
                        value={paymentProvider}
                        onChange={(e) => handlePaymentProviderChange(e.target.value)}
                        className="w-full bg-[#05080e] border border-slate-800 hover:border-slate-700 text-xs text-slate-200 rounded-lg p-2 outline-none cursor-pointer font-sans"
                      >
                        <option value="Stripe">Stripe (Global Default - US Ingress)</option>
                        <option value="PayPal">PayPal Commerce (US Ingress)</option>
                        <option value="Adyen">Adyen Unified Commerce (US Ingress)</option>
                        <option value="Checkout.com">Checkout.com Gateway (US Ingress)</option>
                        <option value="Klarna">Klarna Pay Later (US Ingress)</option>
                        <option value="Conekta">Conekta (Mexico Regional Ingress)</option>
                        <option value="Mercado Pago">Mercado Pago (Brazil Regional Ingress)</option>
                      </select>
                    </div>

                    <div className="grid grid-cols-2 gap-3 bg-slate-950/50 p-3 rounded-lg border border-slate-900">
                      <div>
                        <span className="text-[9px] text-slate-500 font-mono uppercase block">Country Ingress / Currency</span>
                        <span className="text-xs text-slate-200 font-bold font-mono mt-0.5 block truncate">
                          {guestCountry} / {currency}
                        </span>
                      </div>
                      <div>
                        <span className="text-[9px] text-slate-500 font-mono uppercase block">Router Rules Status</span>
                        <span className="text-xs text-emerald-400 font-bold mt-0.5 block truncate">
                          {paymentProvider === 'Conekta' ? 'Mexico Order Ingress' : paymentProvider === 'Mercado Pago' ? 'Brazil Order Ingress' : 'US Order Ingress'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="text-[10px] text-slate-500 border-t border-slate-900 pt-3 flex justify-between items-center">
                  <span>Routing webhook latency: <span className="text-slate-300 font-mono">18ms</span></span>
                  <span className="font-mono text-emerald-400">payments.gateway.router</span>
                </div>
              </div>

            </div>
          </div>
        )}

        {/* VIEW 3: LOCAL RAG EXPLORER */}
        {activeTab === 'rag' && (
          <div className="flex-1 flex flex-col p-6 overflow-y-auto">
            
            {/* RAG HEADER */}
            <div className="mb-6">
              <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                <Database size={16} className="text-emerald-400" />
                Local RAG Knowledge base Explorer
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Query local policy files in the `knowledge_base/` folder. The RAG retriever finds semantic contexts to ground prompt validations.
              </p>
            </div>

            {/* SEARCH BOX */}
            <form onSubmit={executeRagSearch} className="mb-6 flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3.5 top-3 text-slate-500" size={14} />
                <input 
                  type="text"
                  placeholder="Ask policies database (e.g. 'cancellation policy', 'how are refunds issued?', 'check-in time')"
                  value={ragQuery}
                  onChange={(e) => setRagQuery(e.target.value)}
                  className="w-full bg-[#080d16] border border-slate-800 focus:border-emerald-500 rounded-lg py-2.5 pl-10 pr-4 text-xs text-slate-200 outline-none transition-colors font-sans"
                />
              </div>
              <button
                type="submit"
                className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold py-2.5 px-5 rounded-lg cursor-pointer transition-all flex items-center gap-1.5"
              >
                Query RAG
              </button>
            </form>

            {/* RESULTS CONTAINER */}
            <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
              
              {/* RETRIEVED BLOCKS */}
              <div className="border border-slate-800 bg-[#080d16] rounded-xl p-5 flex flex-col min-h-[300px]">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
                  Retrieved Contexts ({ragResults.length} hits)
                </h3>

                {isSearchingRag ? (
                  <div className="flex-1 flex flex-col items-center justify-center text-slate-400 text-xs italic">
                    <RefreshCw className="animate-spin text-emerald-500 mb-2" size={18} />
                    Calculating sentence-transformers embeddings...
                  </div>
                ) : ragResults.length === 0 ? (
                  <div className="flex-1 flex flex-col items-center justify-center text-slate-500 text-xs py-8 text-center max-w-sm mx-auto">
                    <HelpCircle size={24} className="mb-1 text-slate-700" />
                    Enter a query such as <strong className="text-slate-300">"cancellation"</strong>, <strong className="text-slate-300">"refund"</strong>, or <strong className="text-slate-300">"incidentals"</strong> to simulate semantic passage indexing.
                  </div>
                ) : (
                  <div className="space-y-4 overflow-y-auto pr-1">
                    {ragResults.map((hit, index) => (
                      <div key={index} className="bg-[#05080e] p-3.5 rounded-lg border border-slate-800">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[10px] font-mono text-emerald-400 font-semibold bg-emerald-950/40 px-2 py-0.5 rounded">
                            {hit.doc}
                          </span>
                          <span className="text-[10px] text-slate-500 font-mono">Similarity: {(0.88 + (0.1 - index * 0.04)).toFixed(3)}</span>
                        </div>
                        <h4 className="text-xs font-bold text-slate-200 mb-1.5">{hit.title}</h4>
                        <p className="text-xs text-slate-400 leading-relaxed font-sans">{hit.content}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* KNOWLEDGE MAP SUMMARY */}
              <div className="border border-slate-800 bg-[#080d16] rounded-xl p-5 flex flex-col">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
                  Indexed Knowledge Documents
                </h3>
                
                <div className="space-y-3 flex-1 overflow-y-auto pr-1">
                  <div className="p-3 bg-slate-900/40 rounded-lg border border-slate-800/60">
                    <h4 className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                      <span>cancellation_policy.md</span>
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono">Active</span>
                    </h4>
                    <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                      Determines booking late cancellations, standard 48 hours bounds, and penalty rate evaluations.
                    </p>
                  </div>

                  <div className="p-3 bg-slate-900/40 rounded-lg border border-slate-800/60">
                    <h4 className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                      <span>refund_policy.md</span>
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono">Active</span>
                    </h4>
                    <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                      Defines Stripe Sandbox refund authorizations, required tracking variables, and validation schemas.
                    </p>
                  </div>

                  <div className="p-3 bg-slate-900/40 rounded-lg border border-slate-800/60">
                    <h4 className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                      <span>payment_policy.md</span>
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono">Active</span>
                    </h4>
                    <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                      Strict guidelines mandating the LLM/Agent to redirect checkouts securely through unique checkout links.
                    </p>
                  </div>

                  <div className="p-3 bg-slate-900/40 rounded-lg border border-slate-800/60">
                    <h4 className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                      <span>hotel_terms.md</span>
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono">Active</span>
                    </h4>
                    <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                      Check-in requirements, incidental deposits, and general property usage limits.
                    </p>
                  </div>
                </div>
              </div>

            </div>

          </div>
        )}

        {/* VIEW 4: SECURITY & DESIGN */}
        {activeTab === 'docs' && (
          <div className="flex-1 flex flex-col p-6 overflow-y-auto gap-6">
            
            {/* PRINCIPLES */}
            <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5">
              <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2 mb-4">
                <ShieldCheck size={16} className="text-emerald-400" />
                Stripe Sandbox Payment Security Architecture
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-slate-900/40 border border-slate-800/60 rounded-lg">
                  <div className="w-8 h-8 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-2.5 font-bold font-mono text-xs">
                    01
                  </div>
                  <h3 className="text-xs font-bold text-slate-200 mb-1">Indirect Checkout</h3>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    AI agents are strictly forbidden from collecting, storing, or directly prompting credit card numbers. Checkout sessions are generated out-of-band via secure links.
                  </p>
                </div>

                <div className="p-4 bg-slate-900/40 border border-slate-800/60 rounded-lg">
                  <div className="w-8 h-8 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-2.5 font-bold font-mono text-xs">
                    02
                  </div>
                  <h3 className="text-xs font-bold text-slate-200 mb-1">Idempotency Guard</h3>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    Every transactional action submits a unique `idempotency_key` header. Double charges due to network disconnects or browser reloads are completely mitigated.
                  </p>
                </div>

                <div className="p-4 bg-slate-900/40 border border-slate-800/60 rounded-lg">
                  <div className="w-8 h-8 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-2.5 font-bold font-mono text-xs">
                    03
                  </div>
                  <h3 className="text-xs font-bold text-slate-200 mb-1">Webhooks Authority</h3>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    Client-side confirmation state transitions are treated as warnings. The system state is only set to PAID upon cryptographically verified webhook call events.
                  </p>
                </div>
              </div>
            </div>

            {/* FLOW CHART & GITHUB STEPS */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* FLOW SECTION */}
              <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <Cpu size={14} className="text-sky-400" />
                  LangGraph + CrewAI + MCP Approved Flow
                </h3>

                <div className="space-y-4 font-sans text-xs">
                  <div className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-[10px] font-bold border border-emerald-500/20 mt-0.5">
                      1
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-200">POST /reserve/stream</h4>
                      <p className="text-slate-400 text-[11px] mt-0.5">Customer requests Deluxe Suite check-in bounds. Starts server-sent stream.</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-[10px] font-bold border border-emerald-500/20 mt-0.5">
                      2
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-200">LangGraph Execution Nodes</h4>
                      <p className="text-slate-400 text-[11px] mt-0.5">Nodes sequence executes state validations, room availability checks, and price calculations.</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-[10px] font-bold border border-emerald-500/20 mt-0.5">
                      3
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-200">CrewAI Agent (ReservationAgent + PaymentAgent)</h4>
                      <p className="text-slate-400 text-[11px] mt-0.5">ReservationAgent compiles parameters. PaymentAgent calls MCP tool server to initiate link.</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-[10px] font-bold border border-emerald-500/20 mt-0.5">
                      4
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-200">Stripe Webhooks & CONFIRMED State</h4>
                      <p className="text-slate-400 text-[11px] mt-0.5">Customer pays securely. Stripe triggers webhook receiver. State updates to PAID.</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* GIT UPLOAD SECTION */}
              <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Github size={14} className="text-slate-300" />
                  GitHub Repository Upload Guidelines
                </h3>

                <p className="text-xs text-slate-400 leading-normal mb-3">
                  This Phase 1 directory structure has been fully written to the workspace containers. Run these command parameters to link to your portfolio repository:
                </p>

                <div className="bg-[#05080e] rounded-lg border border-slate-900 p-4 font-mono text-xs text-slate-300 space-y-2">
                  <div><span className="text-slate-500"># 1. Initialize local repository</span></div>
                  <div><span className="text-emerald-400">cd</span> hospitality-reservation-payment-agent</div>
                  <div><span className="text-emerald-400">git init</span></div>
                  
                  <div className="pt-2"><span className="text-slate-500"># 2. Add Phase 1 placeholder schemas & policies</span></div>
                  <div><span className="text-emerald-400">git add .</span></div>
                  <div><span className="text-emerald-400">git commit -m</span> <span className="text-amber-200">"feat: initialize Phase 1 hospitality agent skeleton"</span></div>
                  
                  <div className="pt-2"><span className="text-slate-500"># 3. Bind to portfolio repository</span></div>
                  <div><span className="text-emerald-400">git remote add origin</span> https://github.com/aquilinoFrancisco/hospitality-reservation-payment-agent.git</div>
                  <div><span className="text-emerald-400">git branch -M</span> main</div>
                  <div><span className="text-emerald-400">git push -u origin</span> main</div>
                </div>
              </div>

            </div>

          </div>
        )}

      </main>

      {/* COMPLIANCE FOOTER */}
      <footer className="bg-[#060a10] border-t border-slate-800/60 px-6 py-3.5 flex justify-between items-center text-[11px] text-slate-500 font-mono">
        <span>Portfolio Owner: aquilino.francisco@gmail.com</span>
        <span>AI Studio Platform Build • 2026-07-06</span>
      </footer>

    </div>
  );
}