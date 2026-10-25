//Clean-room inspection helper: dumps strings with xrefs, or decompiles chosen functions.
//@category GPowerTeardown
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.data.AbstractStringDataType;
import java.io.*;
import java.util.*;

public class DumpAnova extends GhidraScript {
  @Override
  public void run() throws Exception {
    String[] a = getScriptArgs();
    String mode = a.length > 0 ? a[0] : "strings";
    File out = new File(a.length > 1 ? a[1] : System.getProperty("user.home") + "\\gpower_dump");
    out.mkdirs();
    if (mode.equals("strings")) dumpStrings(out);
    else if (mode.equals("vtable")) vtables(out, a.length > 2 ? a[2] : "");
    else if (mode.equals("doubles")) doubles(out, a.length > 2 ? a[2] : "");
    else decomp(out, a.length > 2 ? a[2] : "");
  }

  void dumpStrings(File out) throws Exception {
    try (PrintWriter w = new PrintWriter(new File(out, "strings_xrefs.tsv"), "UTF-8")) {
      w.println("string_addr\tref_from\tfunc_entry\tstring");
      int n = 0;
      DataIterator dit = currentProgram.getListing().getDefinedData(true);
      while (dit.hasNext()) {
        Data d = dit.next();
        if (!(d.getDataType() instanceof AbstractStringDataType)) continue;
        Object v = d.getValue();
        String s = v == null ? "" : v.toString().replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t");
        if (s.length() < 3) continue;
        Reference[] refs = getReferencesTo(d.getAddress());
        if (refs.length == 0) {
          w.println(d.getAddress() + "\t\t\t" + s);
        }
        for (Reference r : refs) {
          Function f = getFunctionContaining(r.getFromAddress());
          w.println(d.getAddress() + "\t" + r.getFromAddress() + "\t" + (f == null ? "" : f.getEntryPoint().toString()) + "\t" + s);
        }
        n++;
      }
      println("strings written: " + n);
    }
  }

  void vtables(File out, String list) throws Exception {
    ghidra.program.model.mem.Memory mem = currentProgram.getMemory();
    try (PrintWriter w = new PrintWriter(new File(out, "vtables.txt"), "UTF-8")) {
      for (String t : list.split(",")) {
        t = t.trim();
        if (t.isEmpty()) continue;
        Address f = toAddr(t);
        w.println("=== function " + t);
        for (Reference r : getReferencesTo(f)) {
          Address from = r.getFromAddress();
          Data d = getDataContaining(from);
          if (d == null) { w.println("code ref from " + from); continue; }
          // scan back for a label containing 'vftable' (RTTI) or the start of the pointer run
          Address base = from;
          for (int i = 0; i < 0x400; i += 4) {
            Address a = from.subtract(i);
            ghidra.program.model.symbol.Symbol s = currentProgram.getSymbolTable().getPrimarySymbol(a);
            if (s != null && s.getName().toLowerCase().contains("vftable")) { base = a; break; }
          }
          w.println("data ref from " + from + " ; table base guess " + base + " ; slot byte offset " + from.subtract(base));
          for (int i = 0; i < 0x200; i += 4) {
            Address a = base.add(i);
            long v = mem.getInt(a) & 0xffffffffL;
            Address tgt = toAddr(Long.toHexString(v));
            Function fn = tgt == null ? null : getFunctionAt(tgt);
            ghidra.program.model.symbol.Symbol s = currentProgram.getSymbolTable().getPrimarySymbol(a);
            w.println(String.format("%s +0x%03x -> %08x %s %s", a, i, v, fn == null ? "-" : "FUNC", s == null ? "" : s.getName()));
          }
        }
      }
    }
    println("vtables written");
  }

  void doubles(File out, String list) throws Exception {
    try (PrintWriter w = new PrintWriter(new File(out, "doubles.txt"), "UTF-8")) {
      for (String t : list.split(",")) {
        t = t.trim();
        if (t.isEmpty()) continue;
        Address ad = toAddr(t);
        long bits = currentProgram.getMemory().getLong(ad);
        w.println(t + "\t" + Double.longBitsToDouble(bits) + "\t0x" + Long.toHexString(bits));
      }
    }
    println("doubles written");
  }

  void decomp(File out, String list) throws Exception {
    DecompInterface di = new DecompInterface();
    di.openProgram(currentProgram);
    for (String t : list.split(",")) {
      t = t.trim();
      if (t.isEmpty()) continue;
      Address ad = toAddr(t);
      Function f = getFunctionContaining(ad);
      if (f == null) { println("no function at " + t); continue; }
      DecompileResults r = di.decompileFunction(f, 120, monitor);
      File of = new File(out, "dec_" + f.getEntryPoint() + ".c");
      try (PrintWriter w = new PrintWriter(of, "UTF-8")) {
        w.println("// entry " + f.getEntryPoint() + " name " + f.getName());
        StringBuilder sb = new StringBuilder("// callees:");
        for (Function c : f.getCalledFunctions(monitor)) sb.append(" ").append(c.getEntryPoint());
        w.println(sb);
        w.println("// callers:");
        for (Function c : f.getCallingFunctions(monitor)) w.println("//   " + c.getEntryPoint());
        w.println(r.getDecompiledFunction() == null ? "// decompile failed: " + r.getErrorMessage() : r.getDecompiledFunction().getC());
      }
      println("wrote " + of);
    }
  }
}
