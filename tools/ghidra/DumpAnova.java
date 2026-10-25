//Clean-room inspection helper: dumps strings with xrefs, or decompiles chosen functions.
//@category GPowerTeardown
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.Reference;
import ghidra.program.util.DefinedDataIterator;
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
    else decomp(out, a.length > 2 ? a[2] : "");
  }

  void dumpStrings(File out) throws Exception {
    try (PrintWriter w = new PrintWriter(new File(out, "strings_xrefs.tsv"), "UTF-8")) {
      w.println("string_addr\tref_from\tfunc_entry\tstring");
      int n = 0;
      for (Data d : DefinedDataIterator.definedStrings(currentProgram)) {
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
